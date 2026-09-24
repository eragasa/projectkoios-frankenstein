#!/usr/bin/env python3
"""Revalidate an external source declaration against an explicit Git checkout.

The tool reads committed Git objects only. It never imports or executes upstream
Python, runs calculators, changes the checkout, downloads content, or updates a
source declaration. A candidate report is observational and is not acceptance
of a pin change.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = 1


class RevalidationError(RuntimeError):
    """A source declaration or checkout cannot be revalidated safely."""


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise RevalidationError(f"{field} must be a non-empty string")
    return value


def _integer(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise RevalidationError(f"{field} must be a non-negative integer")
    return value


def _safe_relative_path(value: object, field: str) -> str:
    text = _text(value, field)
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or text != path.as_posix():
        raise RevalidationError(f"{field} must be a normalized relative POSIX path")
    return text


def _run_git(checkout: Path, *arguments: str) -> bytes:
    command = ("git", "-C", str(checkout), *arguments)
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
        )
    except FileNotFoundError as error:
        raise RevalidationError("git is required for source revalidation") from error
    except subprocess.CalledProcessError as error:
        detail = error.stderr.decode("utf-8", errors="replace").strip()
        raise RevalidationError(
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
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for statement in module.body:
        value: ast.expr | None = None
        match statement:
            case ast.Assign(targets=targets, value=assigned_value) if any(
                isinstance(target, ast.Name) and target.id == name for target in targets
            ):
                value = assigned_value
            case ast.AnnAssign(
                target=ast.Name(id=target_name), value=assigned_value
            ) if target_name == name:
                value = assigned_value
        if value is not None:
            try:
                return ast.literal_eval(value)
            except (TypeError, ValueError) as error:
                raise RevalidationError(
                    f"{path}: {name} must be a literal value"
                ) from error
    raise RevalidationError(f"{path}: missing literal assignment {name}")


def _identity_table(
    repository_root: Path,
    source_reference: dict[str, Any],
) -> dict[str, tuple[str, int]]:
    selection = source_reference.get("selection", {})
    if not isinstance(selection, dict):
        raise RevalidationError("selection must be a TOML table")

    identity_table_path = selection.get("identity_table")
    if identity_table_path is not None:
        relative_path = _safe_relative_path(
            identity_table_path,
            "selection.identity_table",
        )
        table_path = repository_root / relative_path
        if not table_path.is_file():
            raise RevalidationError(f"identity table does not exist: {relative_path}")
        literal = _literal_assignment(table_path, "SOURCE_FILES")
        if not isinstance(literal, dict):
            raise RevalidationError("SOURCE_FILES must be a dictionary literal")
        result: dict[str, tuple[str, int]] = {}
        for raw_path, raw_identity in literal.items():
            source_path = _safe_relative_path(raw_path, "SOURCE_FILES path")
            if not isinstance(raw_identity, tuple) or len(raw_identity) != 2:
                raise RevalidationError(
                    f"SOURCE_FILES[{source_path!r}] must be a (sha256, size) tuple"
                )
            digest = _text(raw_identity[0], f"SOURCE_FILES[{source_path!r}] sha256")
            size = _integer(raw_identity[1], f"SOURCE_FILES[{source_path!r}] size")
            result[source_path] = (digest, size)
        return result

    source_path_value = selection.get("source_path")
    if source_path_value is None:
        return {}
    source_path = _safe_relative_path(
        source_path_value,
        "selection.source_path",
    )
    digest = _text(selection.get("source_sha256"), "selection.source_sha256")
    size = _integer(selection.get("source_byte_size"), "selection.source_byte_size")
    return {source_path: (digest, size)}


def _file_report(
    checkout: Path,
    revision: str,
    path: str,
    declared_sha256: str,
    declared_byte_size: int,
) -> dict[str, object]:
    payload = _run_git(checkout, "show", f"{revision}:{path}")
    observed_sha256 = hashlib.sha256(payload).hexdigest()
    observed_byte_size = len(payload)
    return {
        "path": path,
        "declared_sha256": declared_sha256,
        "declared_byte_size": declared_byte_size,
        "observed_sha256": observed_sha256,
        "observed_byte_size": observed_byte_size,
        "matches_declared_identity": (
            observed_sha256 == declared_sha256
            and observed_byte_size == declared_byte_size
        ),
    }


def build_report(
    repository_root: Path,
    component: str,
    checkout: Path,
    requested_revision: str | None = None,
) -> dict[str, object]:
    """Build a deterministic identity report without modifying either repository."""

    reference_path = repository_root / "sources" / f"{component}.toml"
    if not reference_path.is_file():
        raise RevalidationError(f"unknown source component: {component}")
    with reference_path.open("rb") as stream:
        reference = tomllib.load(stream)
    if not isinstance(reference, dict):
        raise RevalidationError(f"invalid source declaration: {reference_path}")

    declared_repository = _text(reference.get("repository"), "repository")
    declared_revision = _text(reference.get("revision"), "revision")
    declared_tree = _text(reference.get("tree"), "tree")
    license_path = _safe_relative_path(reference.get("license_path"), "license_path")
    declared_license_sha256 = _text(
        reference.get("license_sha256"),
        "license_sha256",
    )
    selected_identities = _identity_table(repository_root, reference)

    checkout = checkout.resolve()
    if not checkout.is_dir():
        raise RevalidationError(f"checkout does not exist: {checkout}")
    if _git_text(checkout, "rev-parse", "--is-inside-work-tree") != "true":
        raise RevalidationError(f"not a Git working tree: {checkout}")

    observed_repository = _git_text(checkout, "config", "--get", "remote.origin.url")
    repository_matches = _normalize_repository_url(
        observed_repository
    ) == _normalize_repository_url(declared_repository)
    if not repository_matches:
        raise RevalidationError(
            "checkout origin does not match the declared repository: "
            f"{observed_repository!r} != {declared_repository!r}"
        )

    revision_expression = requested_revision or declared_revision
    resolved_revision = _git_text(
        checkout,
        "rev-parse",
        "--verify",
        "--end-of-options",
        f"{revision_expression}^{{commit}}",
    )
    observed_tree = _git_text(
        checkout,
        "rev-parse",
        "--verify",
        "--end-of-options",
        f"{resolved_revision}^{{tree}}",
    )

    license_payload = _run_git(checkout, "show", f"{resolved_revision}:{license_path}")
    observed_license_sha256 = hashlib.sha256(license_payload).hexdigest()
    license_matches = observed_license_sha256 == declared_license_sha256

    selected_files = [
        _file_report(checkout, resolved_revision, path, digest, size)
        for path, (digest, size) in sorted(selected_identities.items())
    ]
    selected_files_match = all(
        bool(item["matches_declared_identity"]) for item in selected_files
    )
    revision_matches = resolved_revision == declared_revision
    tree_matches = observed_tree == declared_tree
    matches_declaration = (
        repository_matches
        and revision_matches
        and tree_matches
        and license_matches
        and selected_files_match
    )

    disposition = (
        "declared_identity_matches"
        if matches_declaration
        else "candidate_identity_differs_not_accepted"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "component": component,
        "disposition": disposition,
        "pin_change_authorized": False,
        "repository": {
            "declared": declared_repository,
            "observed": observed_repository,
            "matches": repository_matches,
        },
        "revision": {
            "requested": revision_expression,
            "declared": declared_revision,
            "observed": resolved_revision,
            "matches": revision_matches,
        },
        "tree": {
            "declared": declared_tree,
            "observed": observed_tree,
            "matches": tree_matches,
        },
        "license": {
            "path": license_path,
            "declared_sha256": declared_license_sha256,
            "observed_sha256": observed_license_sha256,
            "matches": license_matches,
        },
        "selected_files": selected_files,
        "matches_declaration": matches_declaration,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description=(
            "Revalidate a declared external source against committed objects in an "
            "explicit local checkout."
        )
    )
    result.add_argument("component", help="source declaration name under sources/")
    result.add_argument(
        "--checkout",
        type=Path,
        required=True,
        help="explicit operator-managed Git checkout",
    )
    result.add_argument(
        "--revision",
        help="candidate commit or tag; defaults to the declared revision",
    )
    result.add_argument(
        "--report-candidate",
        action="store_true",
        help=(
            "return success for a structurally complete differing identity report; "
            "this does not accept or update the candidate"
        ),
    )
    result.add_argument(
        "--output",
        type=Path,
        help="write deterministic JSON to this path instead of stdout",
    )
    return result


def main(arguments: list[str] | None = None) -> int:
    options = parser().parse_args(arguments)
    repository_root = Path(__file__).resolve().parents[1]
    try:
        report = build_report(
            repository_root=repository_root,
            component=options.component,
            checkout=options.checkout,
            requested_revision=options.revision,
        )
    except RevalidationError as error:
        print(f"revalidation error: {error}", file=sys.stderr)
        return 2

    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if options.output is None:
        sys.stdout.write(encoded)
    else:
        options.output.write_text(encoded, encoding="utf-8")

    if bool(report["matches_declaration"]) or options.report_candidate:
        return 0
    print(
        "source identity differs from the declaration; use --report-candidate only "
        "for an observational candidate report",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
