"""Typed source-reference revalidation models and actionizer."""

from __future__ import annotations

import ast
import hashlib
import subprocess
import tomllib
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any

if __package__.startswith("tools."):
    from tools.base import (
        DataObject,
        DataObjectModel,
        DataObjectRequest,
        DataObjectResult,
        DataObjectSerializer,
        DataObjectVerifier,
    )
else:
    from base import (  # type: ignore[import-not-found,no-redef]
        DataObject,
        DataObjectModel,
        DataObjectRequest,
        DataObjectResult,
        DataObjectSerializer,
        DataObjectVerifier,
    )

SCHEMA_VERSION = 1


class RevalidationError(RuntimeError):
    """A source declaration or checkout cannot be revalidated safely."""


class RevalidationDisposition(StrEnum):
    """Closed outcome vocabulary for a completed source revalidation."""

    DECLARED_IDENTITY_MATCHES = "declared_identity_matches"
    CANDIDATE_IDENTITY_DIFFERS_NOT_ACCEPTED = "candidate_identity_differs_not_accepted"


@dataclass(frozen=True, slots=True)
class SourceReferenceRevalidationRequest(DataObjectRequest):
    """Explicit inputs for one source-reference revalidation."""

    repository_root: Path
    component: str
    checkout: Path
    requested_revision: str | None = None

    def __post_init__(self) -> None:
        if (
            not self.component
            or self.component in {".", ".."}
            or "/" in self.component
            or "\\" in self.component
        ):
            raise RevalidationError("component must be a non-empty file-name stem")
        if self.requested_revision is not None and not self.requested_revision:
            raise RevalidationError("requested_revision must be non-empty when set")


@dataclass(frozen=True, slots=True)
class IdentityComparison(DataObject):
    """Declared and observed identities with their equality result."""

    declared: str
    observed: str
    matches: bool


@dataclass(frozen=True, slots=True)
class RevisionIdentityComparison(IdentityComparison):
    """Revision comparison retaining the operator-requested expression."""

    requested: str


@dataclass(frozen=True, slots=True)
class LicenseIdentityComparison(DataObject):
    """Declared and observed license identities."""

    path: str
    declared_sha256: str
    observed_sha256: str
    matches: bool


@dataclass(frozen=True, slots=True)
class SelectedFileIdentityComparison(DataObject):
    """Declared and observed identity of one selected source file."""

    path: str
    declared_sha256: str
    declared_byte_size: int
    observed_sha256: str
    observed_byte_size: int
    matches_declared_identity: bool


@dataclass(frozen=True, slots=True)
class ExampleTreeIdentityComparison(IdentityComparison):
    """Identity comparison for one selected upstream example tree."""

    path: str


@dataclass(frozen=True, slots=True)
class SourceReferenceRevalidationResponse(DataObjectResult):
    """Immutable closed response for one completed source revalidation."""

    request: SourceReferenceRevalidationRequest
    disposition: RevalidationDisposition
    repository: IdentityComparison
    revision: RevisionIdentityComparison
    tree: IdentityComparison
    license: LicenseIdentityComparison
    selected_files: tuple[SelectedFileIdentityComparison, ...]
    example_trees: tuple[ExampleTreeIdentityComparison, ...]
    matches_declaration: bool
    pin_change_authorized: bool = False
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        expected_match = (
            self.repository.matches
            and self.revision.matches
            and self.tree.matches
            and self.license.matches
            and all(item.matches_declared_identity for item in self.selected_files)
            and all(item.matches for item in self.example_trees)
        )
        expected_disposition = (
            RevalidationDisposition.DECLARED_IDENTITY_MATCHES
            if expected_match
            else RevalidationDisposition.CANDIDATE_IDENTITY_DIFFERS_NOT_ACCEPTED
        )
        if self.matches_declaration is not expected_match:
            raise RevalidationError("matches_declaration contradicts the evidence")
        if self.disposition is not expected_disposition:
            raise RevalidationError("disposition contradicts the evidence")
        if self.pin_change_authorized:
            raise RevalidationError("source revalidation cannot authorize a pin change")
        if self.schema_version != SCHEMA_VERSION:
            raise RevalidationError("response schema_version is unsupported")


@dataclass(frozen=True, slots=True)
class SourceReferenceRevalidationReportModel(DataObjectModel):
    """CLI report model serialized from one revalidation response."""

    schema_version: int
    component: str
    disposition: RevalidationDisposition
    pin_change_authorized: bool
    repository: IdentityComparison
    revision: RevisionIdentityComparison
    tree: IdentityComparison
    license: LicenseIdentityComparison
    selected_files: tuple[SelectedFileIdentityComparison, ...]
    example_trees: tuple[ExampleTreeIdentityComparison, ...]
    matches_declaration: bool


@dataclass(frozen=True, slots=True)
class SourceReferenceRevalidationReportSerializer(
    DataObjectSerializer[
        SourceReferenceRevalidationResponse,
        SourceReferenceRevalidationReportModel,
    ]
):
    """Serialize a typed revalidation response to its CLI report model."""

    def serialize(
        self,
        data_object: SourceReferenceRevalidationResponse,
        /,
    ) -> SourceReferenceRevalidationReportModel:
        return SourceReferenceRevalidationReportModel(
            schema_version=data_object.schema_version,
            component=data_object.request.component,
            disposition=data_object.disposition,
            pin_change_authorized=data_object.pin_change_authorized,
            repository=data_object.repository,
            revision=data_object.revision,
            tree=data_object.tree,
            license=data_object.license,
            selected_files=data_object.selected_files,
            example_trees=data_object.example_trees,
            matches_declaration=data_object.matches_declaration,
        )


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

    result: dict[str, tuple[str, int]] = {}
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
        for raw_path, raw_identity in literal.items():
            source_path = _safe_relative_path(raw_path, "SOURCE_FILES path")
            if not isinstance(raw_identity, tuple) or len(raw_identity) != 2:
                raise RevalidationError(
                    f"SOURCE_FILES[{source_path!r}] must be a (sha256, size) tuple"
                )
            digest = _text(raw_identity[0], f"SOURCE_FILES[{source_path!r}] sha256")
            size = _integer(raw_identity[1], f"SOURCE_FILES[{source_path!r}] size")
            result[source_path] = (digest, size)
    else:
        source_path_value = selection.get("source_path")
        if source_path_value is not None:
            source_path = _safe_relative_path(
                source_path_value,
                "selection.source_path",
            )
            digest = _text(selection.get("source_sha256"), "selection.source_sha256")
            size = _integer(
                selection.get("source_byte_size"),
                "selection.source_byte_size",
            )
            result[source_path] = (digest, size)

    additional_files = selection.get("additional_files", [])
    if not isinstance(additional_files, list):
        raise RevalidationError("selection.additional_files must be an array of tables")
    for index, item in enumerate(additional_files):
        field = f"selection.additional_files[{index}]"
        if not isinstance(item, dict):
            raise RevalidationError(f"{field} must be a table")
        source_path = _safe_relative_path(item.get("path"), f"{field}.path")
        if source_path in result:
            raise RevalidationError(
                f"selected source path is duplicated: {source_path}"
            )
        digest = _text(item.get("sha256"), f"{field}.sha256")
        size = _integer(item.get("byte_size"), f"{field}.byte_size")
        result[source_path] = (digest, size)
    return result


def _example_tree_table(
    repository_root: Path,
    source_reference: dict[str, Any],
) -> dict[str, str]:
    selection = source_reference.get("selection", {})
    if not isinstance(selection, dict):
        raise RevalidationError("selection must be a TOML table")
    inline_table = selection.get("example_trees")
    table_value = selection.get("example_tree_table")
    if inline_table is not None and table_value is not None:
        raise RevalidationError(
            "selection must not define both example_trees and example_tree_table"
        )

    if inline_table is not None:
        if not isinstance(inline_table, dict):
            raise RevalidationError("selection.example_trees must be a table")
        raw_table = inline_table
        field = "selection.example_trees"
    elif table_value is not None:
        relative_path = _safe_relative_path(
            table_value,
            "selection.example_tree_table",
        )
        assignment = _text(
            selection.get("example_tree_assignment"),
            "selection.example_tree_assignment",
        )
        table_path = repository_root / relative_path
        if not table_path.is_file():
            raise RevalidationError(
                f"example tree table does not exist: {relative_path}"
            )
        literal = _literal_assignment(table_path, assignment)
        if not isinstance(literal, dict):
            raise RevalidationError(f"{assignment} must be a dictionary literal")
        raw_table = literal
        field = assignment
    else:
        return {}

    result: dict[str, str] = {}
    for raw_path, raw_tree in raw_table.items():
        path = _safe_relative_path(raw_path, f"{field} path")
        result[path] = _text(raw_tree, f"{field}[{path!r}]")
    return result


def _file_report(
    checkout: Path,
    revision: str,
    path: str,
    declared_sha256: str,
    declared_byte_size: int,
) -> SelectedFileIdentityComparison:
    payload = _run_git(checkout, "show", f"{revision}:{path}")
    observed_sha256 = hashlib.sha256(payload).hexdigest()
    observed_byte_size = len(payload)
    return SelectedFileIdentityComparison(
        path=path,
        declared_sha256=declared_sha256,
        declared_byte_size=declared_byte_size,
        observed_sha256=observed_sha256,
        observed_byte_size=observed_byte_size,
        matches_declared_identity=(
            observed_sha256 == declared_sha256
            and observed_byte_size == declared_byte_size
        ),
    )


def _build_response(
    request: SourceReferenceRevalidationRequest,
) -> SourceReferenceRevalidationResponse:
    repository_root = request.repository_root
    component = request.component
    checkout = request.checkout
    requested_revision = request.requested_revision

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
    example_tree_identities = _example_tree_table(repository_root, reference)

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

    selected_files = tuple(
        _file_report(checkout, resolved_revision, path, digest, size)
        for path, (digest, size) in sorted(selected_identities.items())
    )
    selected_files_match = all(
        item.matches_declared_identity for item in selected_files
    )
    example_trees: list[ExampleTreeIdentityComparison] = []
    for path, declared_example_tree in sorted(example_tree_identities.items()):
        observed_example_tree = _git_text(
            checkout,
            "rev-parse",
            "--verify",
            "--end-of-options",
            f"{resolved_revision}:{path}",
        )
        example_trees.append(
            ExampleTreeIdentityComparison(
                path=path,
                declared=declared_example_tree,
                observed=observed_example_tree,
                matches=observed_example_tree == declared_example_tree,
            )
        )
    example_trees_match = all(item.matches for item in example_trees)
    revision_matches = resolved_revision == declared_revision
    tree_matches = observed_tree == declared_tree
    matches_declaration = (
        repository_matches
        and revision_matches
        and tree_matches
        and license_matches
        and selected_files_match
        and example_trees_match
    )

    disposition = (
        RevalidationDisposition.DECLARED_IDENTITY_MATCHES
        if matches_declaration
        else RevalidationDisposition.CANDIDATE_IDENTITY_DIFFERS_NOT_ACCEPTED
    )
    return SourceReferenceRevalidationResponse(
        request=request,
        disposition=disposition,
        repository=IdentityComparison(
            declared=declared_repository,
            observed=observed_repository,
            matches=repository_matches,
        ),
        revision=RevisionIdentityComparison(
            requested=revision_expression,
            declared=declared_revision,
            observed=resolved_revision,
            matches=revision_matches,
        ),
        tree=IdentityComparison(
            declared=declared_tree,
            observed=observed_tree,
            matches=tree_matches,
        ),
        license=LicenseIdentityComparison(
            path=license_path,
            declared_sha256=declared_license_sha256,
            observed_sha256=observed_license_sha256,
            matches=license_matches,
        ),
        selected_files=selected_files,
        example_trees=tuple(example_trees),
        matches_declaration=matches_declaration,
    )


@dataclass(frozen=True, slots=True)
class SourceReferenceRevalidator(
    DataObjectVerifier[
        SourceReferenceRevalidationRequest,
        SourceReferenceRevalidationResponse,
    ]
):
    """Revalidate one explicit source request against committed Git objects."""

    def actionize(
        self,
        request: SourceReferenceRevalidationRequest,
        /,
    ) -> SourceReferenceRevalidationResponse:
        """Return an immutable response without modifying either repository."""

        return _build_response(request)
