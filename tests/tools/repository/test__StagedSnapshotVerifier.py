from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.repository.staged_snapshot import (
    StagedSnapshotVerificationCommand,
    StagedSnapshotVerificationError,
    StagedSnapshotVerificationRequest,
    StagedSnapshotVerifier,
)


def _git(repository: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(repository), *arguments),
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


class StagedSnapshotVerifierTest(unittest.TestCase):
    def test_verifies_staged_content_without_working_tree_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            _git(repository, "init", "--quiet")
            tracked = repository / "tracked.txt"
            tracked.write_text("staged\n", encoding="utf-8")
            _git(repository, "add", "tracked.txt")
            tracked.write_text("unstaged\n", encoding="utf-8")
            (repository / "untracked.txt").write_text(
                "not in the index\n",
                encoding="utf-8",
            )
            command = StagedSnapshotVerificationCommand(
                label="inspect-index",
                arguments=(
                    sys.executable,
                    "-c",
                    (
                        "from pathlib import Path; "
                        "assert Path('tracked.txt').read_text() == 'staged\\n'; "
                        "assert not Path('untracked.txt').exists()"
                    ),
                ),
            )
            request = StagedSnapshotVerificationRequest(
                repository_root=repository,
                commands=(command,),
            )

            result = StagedSnapshotVerifier().actionize(request)

            self.assertIs(result.request, request)
            self.assertEqual(result.completed_commands, ("inspect-index",))
            self.assertEqual(result.staged_tree, _git(repository, "write-tree"))
            self.assertEqual(tracked.read_text(encoding="utf-8"), "unstaged\n")

    def test_reports_the_failing_verification_command(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            _git(repository, "init", "--quiet")
            (repository / "tracked.txt").write_text("staged\n", encoding="utf-8")
            _git(repository, "add", "tracked.txt")
            request = StagedSnapshotVerificationRequest(
                repository_root=repository,
                commands=(
                    StagedSnapshotVerificationCommand(
                        label="fails",
                        arguments=(sys.executable, "-c", "raise SystemExit(7)"),
                    ),
                ),
            )

            with self.assertRaisesRegex(
                StagedSnapshotVerificationError,
                "'fails'.*exit status 7",
            ):
                StagedSnapshotVerifier().actionize(request)

    def test_requires_an_explicit_command_sequence(self) -> None:
        with self.assertRaisesRegex(
            StagedSnapshotVerificationError,
            "at least one",
        ):
            StagedSnapshotVerificationRequest(
                repository_root=Path("."),
                commands=(),
            )


if __name__ == "__main__":
    unittest.main()
