#!/usr/bin/env python3
"""Run the maintained verification sequence against the exact Git index."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__:
    from tools.repository.staged_snapshot import (
        StagedSnapshotVerificationCommand,
        StagedSnapshotVerificationError,
        StagedSnapshotVerificationRequest,
        StagedSnapshotVerifier,
    )
else:
    from repository.staged_snapshot import (  # type: ignore[import-not-found,no-redef]
        StagedSnapshotVerificationCommand,
        StagedSnapshotVerificationError,
        StagedSnapshotVerificationRequest,
        StagedSnapshotVerifier,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository",
        type=Path,
        default=Path.cwd(),
        help="Git worktree root; defaults to the current directory",
    )
    parser.add_argument(
        "--python",
        type=Path,
        default=Path(sys.executable),
        help="Python executable containing the development dependencies",
    )
    return parser


def _commands(python: Path) -> tuple[StagedSnapshotVerificationCommand, ...]:
    executable = str(python.absolute())
    return (
        StagedSnapshotVerificationCommand(
            label="tests",
            arguments=(executable, "-m", "pytest", "-q"),
        ),
        StagedSnapshotVerificationCommand(
            label="lint",
            arguments=(executable, "-m", "ruff", "check", "."),
        ),
        StagedSnapshotVerificationCommand(
            label="format",
            arguments=(
                executable,
                "-m",
                "ruff",
                "format",
                "--check",
                "src",
                "tests",
                "tools",
            ),
        ),
        StagedSnapshotVerificationCommand(
            label="types",
            arguments=(
                executable,
                "-m",
                "mypy",
                "--strict",
                "src/projectkoios/frankensteins",
            ),
            environment=(("MYPYPATH", "src"),),
        ),
        StagedSnapshotVerificationCommand(
            label="wheel",
            arguments=(executable, "-m", "build", "--wheel"),
        ),
    )


def main(arguments: list[str] | None = None) -> int:
    options = _parser().parse_args(arguments)
    request = StagedSnapshotVerificationRequest(
        repository_root=options.repository,
        commands=_commands(options.python),
    )
    try:
        result = StagedSnapshotVerifier().actionize(request)
    except StagedSnapshotVerificationError as error:
        print(f"staged-snapshot verification error: {error}", file=sys.stderr)
        return 1
    print(f"verified staged tree {result.staged_tree}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
