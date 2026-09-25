"""Read constrained Python literal assignments without executing Python code."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

if __package__.startswith("tools."):
    from tools.base import (
        DataObject,
        DataObjectActionizer,
        DataObjectRequest,
        DataObjectResult,
    )
else:
    from base import (  # type: ignore[import-not-found,no-redef]
        DataObject,
        DataObjectActionizer,
        DataObjectRequest,
        DataObjectResult,
    )


class PythonLiteralAssignmentError(RuntimeError):
    """A Python source assignment cannot be inspected safely."""


@dataclass(frozen=True, slots=True)
class PythonStringMappingEntry(DataObject):
    """One immutable string key/value pair read from Python syntax."""

    key: str
    value: str

    def __post_init__(self) -> None:
        if not self.key:
            raise PythonLiteralAssignmentError("mapping keys must be non-empty strings")
        if not self.value:
            raise PythonLiteralAssignmentError(
                "mapping values must be non-empty strings"
            )


@dataclass(frozen=True, slots=True)
class PythonStringMappingAssignmentRequest(DataObjectRequest):
    """Request one named string-mapping literal from a Python source file."""

    source_path: Path
    assignment_name: str

    def __post_init__(self) -> None:
        if not self.assignment_name.isidentifier():
            raise PythonLiteralAssignmentError(
                "assignment_name must be a Python identifier"
            )


@dataclass(frozen=True, slots=True)
class PythonStringMappingAssignmentResult(DataObjectResult):
    """Immutable entries read from one Python literal assignment."""

    request: PythonStringMappingAssignmentRequest
    entries: tuple[PythonStringMappingEntry, ...]


def _assignment_value(
    syntax_tree: ast.Module,
    assignment_name: str,
) -> ast.expr:
    values: list[ast.expr] = []
    for node in syntax_tree.body:
        if isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == assignment_name
                and node.value is not None
            ):
                values.append(node.value)
            continue
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == assignment_name
            for target in node.targets
        ):
            values.append(node.value)
    if not values:
        raise PythonLiteralAssignmentError(f"missing assignment {assignment_name!r}")
    if len(values) != 1:
        raise PythonLiteralAssignmentError(
            f"assignment {assignment_name!r} must occur exactly once"
        )
    return values[0]


def _string_literal(node: ast.expr, description: str) -> str:
    try:
        value = ast.literal_eval(node)
    except (TypeError, ValueError) as error:
        raise PythonLiteralAssignmentError(
            f"{description} must be a string literal"
        ) from error
    if not isinstance(value, str) or not value:
        raise PythonLiteralAssignmentError(
            f"{description} must be a non-empty string literal"
        )
    return value


@dataclass(frozen=True, slots=True)
class PythonStringMappingAssignmentReader(
    DataObjectActionizer[
        PythonStringMappingAssignmentRequest,
        PythonStringMappingAssignmentResult,
    ]
):
    """Read one string-mapping literal without importing its source module."""

    def actionize(
        self,
        request: PythonStringMappingAssignmentRequest,
        /,
    ) -> PythonStringMappingAssignmentResult:
        try:
            source = request.source_path.read_text(encoding="utf-8")
            syntax_tree = ast.parse(source, filename=str(request.source_path))
        except (OSError, UnicodeError, SyntaxError) as error:
            raise PythonLiteralAssignmentError(
                f"cannot parse Python source {request.source_path}: {error}"
            ) from error

        value = _assignment_value(syntax_tree, request.assignment_name)
        if not isinstance(value, ast.Dict):
            raise PythonLiteralAssignmentError(
                f"assignment {request.assignment_name!r} must be a dictionary literal"
            )

        entries: list[PythonStringMappingEntry] = []
        observed_keys: set[str] = set()
        for key_node, value_node in zip(value.keys, value.values, strict=True):
            if key_node is None:
                raise PythonLiteralAssignmentError(
                    "dictionary unpacking is not permitted"
                )
            key = _string_literal(key_node, "mapping key")
            if key in observed_keys:
                raise PythonLiteralAssignmentError(f"duplicate mapping key {key!r}")
            observed_keys.add(key)
            entries.append(
                PythonStringMappingEntry(
                    key=key,
                    value=_string_literal(value_node, f"value for {key!r}"),
                )
            )

        return PythonStringMappingAssignmentResult(
            request=request,
            entries=tuple(entries),
        )


__all__ = [
    "PythonLiteralAssignmentError",
    "PythonStringMappingAssignmentReader",
    "PythonStringMappingAssignmentRequest",
    "PythonStringMappingAssignmentResult",
    "PythonStringMappingEntry",
]
