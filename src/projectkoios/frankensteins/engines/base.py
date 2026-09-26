"""Nominal identities for bounded historical example engines."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath

_ENGINE_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_GIT_SHA1 = re.compile(r"[0-9a-f]{40}")


def _validate_entrypoint(entrypoint: str) -> None:
    path = PurePosixPath(entrypoint)
    if (
        type(entrypoint) is not str
        or not entrypoint
        or entrypoint != path.as_posix()
        or len(path.parts) != 1
        or path.suffix != ".py"
    ):
        raise ValueError("each entrypoint must be a root-level Python filename")


@dataclass(frozen=True, slots=True)
class BaseEngine:
    """Represent one immutable source-qualified historical engine identity."""

    engine_name: str
    example_root: str
    example_tree: str
    entrypoints: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            type(self.engine_name) is not str
            or _ENGINE_NAME.fullmatch(self.engine_name) is None
        ):
            raise ValueError("engine_name must be a lowercase hyphenated identifier")
        self._validate_example_root()
        if (
            type(self.example_tree) is not str
            or _GIT_SHA1.fullmatch(self.example_tree) is None
        ):
            raise ValueError("example_tree must be an exact Git SHA-1 tree")
        if type(self.entrypoints) is not tuple or not self.entrypoints:
            raise ValueError("entrypoints must be a nonempty tuple")
        if len(self.entrypoints) != len(set(self.entrypoints)):
            raise ValueError("entrypoints must be unique")
        for entrypoint in self.entrypoints:
            _validate_entrypoint(entrypoint)

    def _validate_example_root(self) -> None:
        path = PurePosixPath(self.example_root)
        if (
            type(self.example_root) is not str
            or not self.example_root
            or self.example_root != path.as_posix()
            or path.is_absolute()
            or len(path.parts) < 2
            or path.parts[0] != "examples"
            or "." in path.parts
            or ".." in path.parts
        ):
            raise ValueError("example_root must be normalized below examples/")

    def _validate_engine_name(self, value: str, field_name: str) -> None:
        if type(value) is not str or _ENGINE_NAME.fullmatch(value) is None:
            raise ValueError(f"{field_name} must be a lowercase hyphenated identifier")
