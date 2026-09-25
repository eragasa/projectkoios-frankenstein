#!/usr/bin/env python3
"""Vendor an authorized source selection from committed Git objects.

The tool never reads an upstream working tree, executes upstream code, changes a
source pin, or downloads content. A recipe maps source paths authorized by an
existing source declaration to repository-relative destinations. ``--sync``
extracts exact blobs and refreshes provenance; ``--check`` is read-only.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = 1


class VendoringError(RuntimeError):
    """A vendoring recipe, source checkout, or destination is invalid."""


@dataclass(frozen=True)
class FileSelection:
    role: str
    source: str
    destination: str


@dataclass(frozen=True)
class DerivedFile:
    role: str
    based_on: str
    destination: str
    local_modifications: str


@dataclass(frozen=True)
class MaintainedFile:
    role: str
    destination: str
    origin: str


@dataclass(frozen=True)
class Recipe:
    component: str
    provenance_path: str
    source_example: str
    representation: str
    files: tuple[FileSelection, ...]
    derived_files: tuple[DerivedFile, ...]
    maintained_files: tuple[MaintainedFile, ...]


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise VendoringError(f"{field} must be a non-empty string")
    return value


def _safe_path(value: object, field: str) -> str:
    text = _text(value, field)
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or text != path.as_posix():
        raise VendoringError(f"{field} must be a normalized relative POSIX path")
    return text


def _table_list(document: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = document.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise VendoringError(f"{key} must be an array of tables")
    return value


def load_recipe(path: Path) -> Recipe:
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise VendoringError(f"cannot read recipe {path}: {error}") from error
    if document.get("schema_version") != SCHEMA_VERSION:
        raise VendoringError(f"recipe schema_version must be {SCHEMA_VERSION}")

    provenance = document.get("provenance")
    if not isinstance(provenance, dict):
        raise VendoringError("provenance must be a table")

    files = tuple(
        FileSelection(
            role=_text(item.get("role"), f"files[{index}].role"),
            source=_safe_path(item.get("source"), f"files[{index}].source"),
            destination=_safe_path(
                item.get("destination"), f"files[{index}].destination"
            ),
        )
        for index, item in enumerate(_table_list(document, "files"))
    )
    if not files:
        raise VendoringError("recipe must select at least one file")

    derived_files = tuple(
        DerivedFile(
            role=_text(item.get("role"), f"derived_files[{index}].role"),
            based_on=_safe_path(
                item.get("based_on"), f"derived_files[{index}].based_on"
            ),
            destination=_safe_path(
                item.get("destination"), f"derived_files[{index}].destination"
            ),
            local_modifications=_text(
                item.get("local_modifications"),
                f"derived_files[{index}].local_modifications",
            ),
        )
        for index, item in enumerate(_table_list(document, "derived_files"))
    )
    maintained_files = tuple(
        MaintainedFile(
            role=_text(item.get("role"), f"maintained_files[{index}].role"),
            destination=_safe_path(
                item.get("destination"), f"maintained_files[{index}].destination"
            ),
            origin=_text(item.get("origin"), f"maintained_files[{index}].origin"),
        )
        for index, item in enumerate(_table_list(document, "maintained_files"))
    )

    destinations = [
        *(item.destination for item in files),
        *(item.destination for item in derived_files),
        *(item.destination for item in maintained_files),
    ]
    if len(destinations) != len(set(destinations)):
        raise VendoringError("recipe destination paths must be unique")

    return Recipe(
        component=_text(document.get("component"), "component"),
        provenance_path=_safe_path(provenance.get("path"), "provenance.path"),
        source_example=_safe_path(
            provenance.get("source_example"), "provenance.source_example"
        ),
        representation=_text(
            provenance.get("representation"), "provenance.representation"
        ),
        files=files,
        derived_files=derived_files,
        maintained_files=maintained_files,
    )


def _run_git(checkout: Path, *arguments: str) -> bytes:
    try:
        completed = subprocess.run(
            ("git", "-C", os.fspath(checkout), *arguments),
            check=True,
            capture_output=True,
        )
    except FileNotFoundError as error:
        raise VendoringError("git is required for vendoring") from error
    except subprocess.CalledProcessError as error:
        detail = error.stderr.decode("utf-8", errors="replace").strip()
        raise VendoringError(
            f"git command failed ({' '.join(arguments)}): {detail}"
        ) from error
    return completed.stdout


def _git_text(checkout: Path, *arguments: str) -> str:
    return _run_git(checkout, *arguments).decode("utf-8").strip()


def _normalize_repository_url(url: str) -> str:
    normalized = url.strip().rstrip("/")
    if normalized.startswith("git@github.com:"):
        normalized = "https://github.com/" + normalized.removeprefix("git@github.com:")
    elif normalized.startswith("ssh://git@github.com/"):
        normalized = "https://github.com/" + normalized.removeprefix(
            "ssh://git@github.com/"
        )
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    return normalized


def _literal_assignment(path: Path, name: str) -> object:
    module = ast.parse(path.read_text(encoding="utf-8"), filename=os.fspath(path))
    for statement in module.body:
        value: ast.expr | None = None
        if (
            isinstance(statement, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == name
                for target in statement.targets
            )
        ) or (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.target.id == name
        ):
            value = statement.value
        if value is not None:
            try:
                return ast.literal_eval(value)
            except (TypeError, ValueError) as error:
                raise VendoringError(
                    f"{path}: {name} must be a literal value"
                ) from error
    raise VendoringError(f"{path}: missing literal assignment {name}")


def _authorized_paths(
    repository_root: Path, source: dict[str, Any]
) -> tuple[dict[str, tuple[str, int]], tuple[str, ...]]:
    selection = source.get("selection")
    if not isinstance(selection, dict):
        raise VendoringError("source selection must be a table")

    identities: dict[str, tuple[str, int]] = {}
    primary_path = selection.get("source_path")
    if primary_path is not None:
        path = _safe_path(primary_path, "selection.source_path")
        digest = _text(selection.get("source_sha256"), "selection.source_sha256")
        size = selection.get("source_byte_size")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise VendoringError("selection.source_byte_size must be non-negative")
        identities[path] = (digest, size)

    for index, item in enumerate(selection.get("additional_files", [])):
        if not isinstance(item, dict):
            raise VendoringError(f"selection.additional_files[{index}] must be a table")
        path = _safe_path(item.get("path"), f"selection.additional_files[{index}].path")
        digest = _text(
            item.get("sha256"), f"selection.additional_files[{index}].sha256"
        )
        size = item.get("byte_size")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise VendoringError(
                f"selection.additional_files[{index}].byte_size must be non-negative"
            )
        identities[path] = (digest, size)

    inline_table = selection.get("example_trees")
    table_value = selection.get("example_tree_table")
    if inline_table is not None and table_value is not None:
        raise VendoringError(
            "selection must not define both example_trees and example_tree_table"
        )

    if inline_table is not None:
        if not isinstance(inline_table, dict):
            raise VendoringError("selection.example_trees must be a table")
        raw_roots = inline_table
        field = "selection.example_trees"
    elif table_value is not None:
        table_path = repository_root / _safe_path(
            table_value, "selection.example_tree_table"
        )
        assignment = _text(
            selection.get("example_tree_assignment"),
            "selection.example_tree_assignment",
        )
        literal = _literal_assignment(table_path, assignment)
        if not isinstance(literal, dict):
            raise VendoringError(f"{assignment} must be a dictionary literal")
        raw_roots = literal
        field = assignment
    else:
        raw_roots = {}
        field = "selection.example_trees"

    example_roots = tuple(_safe_path(path, f"{field} path") for path in raw_roots)
    return identities, example_roots


def _is_under(path: str, root: str) -> bool:
    source = PurePosixPath(path)
    parent = PurePosixPath(root)
    return source == parent or parent in source.parents


def _destination(repository_root: Path, relative_path: str) -> Path:
    destination = repository_root / relative_path
    resolved_parent = destination.parent.resolve()
    try:
        resolved_parent.relative_to(repository_root.resolve())
    except ValueError as error:
        raise VendoringError(
            f"destination escapes repository: {relative_path}"
        ) from error
    if destination.is_symlink():
        raise VendoringError(f"destination must not be a symlink: {relative_path}")
    return destination


def _identity(payload: bytes) -> tuple[str, int]:
    return hashlib.sha256(payload).hexdigest(), len(payload)


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.chmod(0o644)
    temporary.replace(path)


def _source_document(path: Path) -> dict[str, Any]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise VendoringError(
            f"cannot read source declaration {path}: {error}"
        ) from error


def _validate_checkout(checkout: Path, source: dict[str, Any]) -> tuple[str, str]:
    revision = _text(source.get("revision"), "revision")
    declared_tree = _text(source.get("tree"), "tree")
    resolved_revision = _git_text(checkout, "rev-parse", f"{revision}^{{commit}}")
    if resolved_revision != revision:
        raise VendoringError("source revision does not resolve to its declared commit")
    observed_tree = _git_text(checkout, "rev-parse", f"{revision}^{{tree}}")
    if observed_tree != declared_tree:
        raise VendoringError("source revision tree does not match the declaration")
    declared_repository = _normalize_repository_url(
        _text(source.get("repository"), "repository")
    )
    observed_repository = _normalize_repository_url(
        _git_text(checkout, "remote", "get-url", "origin")
    )
    if observed_repository != declared_repository:
        raise VendoringError("checkout origin does not match the source declaration")
    return revision, declared_tree


def _blob(checkout: Path, revision: str, source_path: str) -> tuple[bytes, str, str]:
    payload = _run_git(checkout, "cat-file", "blob", f"{revision}:{source_path}")
    object_id = _git_text(checkout, "rev-parse", f"{revision}:{source_path}")
    tree_entry = _git_text(checkout, "ls-tree", revision, "--", source_path)
    fields = tree_entry.split(maxsplit=3)
    if len(fields) != 4 or fields[1] != "blob" or fields[2] != object_id:
        raise VendoringError(f"could not verify Git tree entry: {source_path}")
    return payload, object_id, fields[0]


def _read_required(path: Path, field: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as error:
        raise VendoringError(f"cannot read {field} {path}: {error}") from error


def vendor(
    *,
    repository_root: Path,
    recipe_path: Path,
    checkout: Path,
    sync: bool,
) -> None:
    recipe = load_recipe(recipe_path)
    source_path = repository_root / "sources" / f"{recipe.component}.toml"
    source = _source_document(source_path)
    if source.get("component") != recipe.component:
        raise VendoringError("recipe component does not match source declaration")
    revision, tree = _validate_checkout(checkout, source)
    identities, example_roots = _authorized_paths(repository_root, source)

    file_records: list[dict[str, object]] = []
    mismatches: list[str] = []
    for selection in recipe.files:
        payload, object_id, git_mode = _blob(checkout, revision, selection.source)
        digest, size = _identity(payload)
        declared_identity = identities.get(selection.source)
        authorized_by_tree = any(
            _is_under(selection.source, root) for root in example_roots
        )
        if declared_identity is None and not authorized_by_tree:
            raise VendoringError(
                f"source path is not authorized by the declaration: {selection.source}"
            )
        if declared_identity is not None and declared_identity != (digest, size):
            raise VendoringError(
                f"declared identity does not match source blob: {selection.source}"
            )

        destination = _destination(repository_root, selection.destination)
        if sync:
            _atomic_write(destination, payload)
        elif not destination.is_file() or destination.read_bytes() != payload:
            mismatches.append(selection.destination)
        file_records.append(
            {
                "role": selection.role,
                "original_path": selection.source,
                "vendored_path": selection.destination,
                "git_mode": git_mode,
                "git_blob_oid": object_id,
                "sha256": digest,
                "byte_size": size,
                "local_modifications": "None",
            }
        )

    derived_records: list[dict[str, object]] = []
    for derived in recipe.derived_files:
        upstream, object_id, _ = _blob(checkout, revision, derived.based_on)
        destination = _destination(repository_root, derived.destination)
        payload = _read_required(destination, "derived file")
        digest, size = _identity(payload)
        derived_records.append(
            {
                "role": derived.role,
                "based_on_original_path": derived.based_on,
                "based_on_git_blob_oid": object_id,
                "based_on_sha256": hashlib.sha256(upstream).hexdigest(),
                "vendored_path": derived.destination,
                "sha256": digest,
                "byte_size": size,
                "local_modifications": derived.local_modifications,
            }
        )

    maintained_records: list[dict[str, object]] = []
    for maintained in recipe.maintained_files:
        destination = _destination(repository_root, maintained.destination)
        payload = _read_required(destination, "maintained file")
        digest, size = _identity(payload)
        maintained_records.append(
            {
                "role": maintained.role,
                "path": maintained.destination,
                "sha256": digest,
                "byte_size": size,
                "origin": maintained.origin,
            }
        )

    provenance_path = _destination(repository_root, recipe.provenance_path)
    if provenance_path.is_file():
        try:
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise VendoringError(f"cannot read provenance manifest: {error}") from error
        if not isinstance(provenance, dict):
            raise VendoringError("provenance manifest must contain an object")
    else:
        provenance = {}
    provenance.update(
        {
            "schema_version": SCHEMA_VERSION,
            "component": recipe.component,
            "repository": _text(source.get("repository"), "repository"),
            "revision": revision,
            "tree": tree,
            "release_tag": _text(source.get("release_tag"), "release_tag"),
            "license_path": _safe_path(source.get("license_path"), "license_path"),
            "license_sha256": _text(source.get("license_sha256"), "license_sha256"),
            "source_example": recipe.source_example,
            "representation": recipe.representation,
            "files": file_records,
            "derived_files": derived_records,
            "maintained_files": maintained_records,
        }
    )
    rendered = (json.dumps(provenance, indent=2) + "\n").encode()
    if sync:
        _atomic_write(provenance_path, rendered)
    elif not provenance_path.is_file() or provenance_path.read_bytes() != rendered:
        mismatches.append(recipe.provenance_path)

    if mismatches:
        details = "\n".join(f"- {path}" for path in mismatches)
        raise VendoringError(f"vendored selection is out of date:\n{details}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recipe", type=Path)
    parser.add_argument("--checkout", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--sync", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    repository_root = Path(__file__).resolve().parents[1]
    recipe_path = arguments.recipe
    if not recipe_path.is_absolute():
        recipe_path = repository_root / recipe_path
    try:
        vendor(
            repository_root=repository_root,
            recipe_path=recipe_path,
            checkout=arguments.checkout.resolve(),
            sync=arguments.sync,
        )
    except VendoringError as error:
        print(f"vendoring error: {error}", file=sys.stderr)
        return 1
    message = (
        "vendored selection synchronized"
        if arguments.sync
        else "vendored selection matches"
    )
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
