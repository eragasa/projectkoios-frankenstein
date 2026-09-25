"""Materialize and verify the exact contents of the Git index."""

from __future__ import annotations

import os
import subprocess
import tempfile
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


class StagedSnapshotVerificationError(RuntimeError):
    """The staged repository snapshot could not be verified."""


@dataclass(frozen=True, slots=True)
class StagedSnapshotVerificationCommand(DataObject):
    """One explicitly selected command executed inside the staged snapshot."""

    label: str
    arguments: tuple[str, ...]
    environment: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.label:
            raise StagedSnapshotVerificationError("command label must be non-empty")
        if not self.arguments or not self.arguments[0]:
            raise StagedSnapshotVerificationError(
                "command arguments must identify an executable"
            )
        names: set[str] = set()
        for name, _value in self.environment:
            if not name or name in names:
                raise StagedSnapshotVerificationError(
                    "command environment names must be non-empty and unique"
                )
            names.add(name)


@dataclass(frozen=True, slots=True)
class StagedSnapshotVerificationRequest(DataObjectRequest):
    """Explicit repository and command sequence for staged verification."""

    repository_root: Path
    commands: tuple[StagedSnapshotVerificationCommand, ...]

    def __post_init__(self) -> None:
        if not self.commands:
            raise StagedSnapshotVerificationError(
                "at least one verification command is required"
            )
        labels = tuple(command.label for command in self.commands)
        if len(set(labels)) != len(labels):
            raise StagedSnapshotVerificationError(
                "verification command labels must be unique"
            )


@dataclass(frozen=True, slots=True)
class StagedSnapshotVerificationResult(DataObjectResult):
    """Closed evidence that every requested command passed one staged tree."""

    request: StagedSnapshotVerificationRequest
    staged_tree: str
    completed_commands: tuple[str, ...]

    def __post_init__(self) -> None:
        expected = tuple(command.label for command in self.request.commands)
        if self.completed_commands != expected:
            raise StagedSnapshotVerificationError(
                "completed commands do not match the requested sequence"
            )
        if len(self.staged_tree) not in {40, 64} or any(
            character not in "0123456789abcdef" for character in self.staged_tree
        ):
            raise StagedSnapshotVerificationError(
                "staged_tree must be a hexadecimal Git object identity"
            )


def _run_git(repository_root: Path, *arguments: str) -> str:
    try:
        completed = subprocess.run(
            ("git", "-C", str(repository_root), *arguments),
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        detail = (
            error.stderr.strip()
            if isinstance(error, subprocess.CalledProcessError)
            else str(error)
        )
        raise StagedSnapshotVerificationError(
            f"git {' '.join(arguments)} failed: {detail}"
        ) from error
    return completed.stdout.strip()


@dataclass(frozen=True, slots=True)
class StagedSnapshotVerifier(
    DataObjectActionizer[
        StagedSnapshotVerificationRequest,
        StagedSnapshotVerificationResult,
    ]
):
    """Run explicit checks against a temporary checkout of the Git index."""

    def actionize(
        self,
        request: StagedSnapshotVerificationRequest,
        /,
    ) -> StagedSnapshotVerificationResult:
        repository_root = request.repository_root.resolve()
        observed_root = Path(
            _run_git(repository_root, "rev-parse", "--show-toplevel")
        ).resolve()
        if observed_root != repository_root:
            raise StagedSnapshotVerificationError(
                f"repository_root is not a Git worktree root: {repository_root}"
            )

        staged_tree = _run_git(repository_root, "write-tree")
        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory)
            _run_git(
                repository_root,
                "checkout-index",
                "--all",
                f"--prefix={snapshot}{os.sep}",
            )
            for command in request.commands:
                environment = os.environ.copy()
                environment["PYTHONPATH"] = str(snapshot / "src")
                environment.update(command.environment)
                try:
                    completed = subprocess.run(
                        command.arguments,
                        cwd=snapshot,
                        env=environment,
                        check=False,
                    )
                except OSError as error:
                    raise StagedSnapshotVerificationError(
                        f"verification command {command.label!r} could not run: {error}"
                    ) from error
                if completed.returncode != 0:
                    raise StagedSnapshotVerificationError(
                        f"verification command {command.label!r} failed with "
                        f"exit status {completed.returncode}"
                    )

        observed_tree = _run_git(repository_root, "write-tree")
        if observed_tree != staged_tree:
            raise StagedSnapshotVerificationError(
                "the Git index changed during staged-snapshot verification"
            )
        _run_git(repository_root, "diff", "--cached", "--check")
        return StagedSnapshotVerificationResult(
            request=request,
            staged_tree=staged_tree,
            completed_commands=tuple(command.label for command in request.commands),
        )


__all__ = [
    "StagedSnapshotVerificationCommand",
    "StagedSnapshotVerificationError",
    "StagedSnapshotVerificationRequest",
    "StagedSnapshotVerificationResult",
    "StagedSnapshotVerifier",
]
