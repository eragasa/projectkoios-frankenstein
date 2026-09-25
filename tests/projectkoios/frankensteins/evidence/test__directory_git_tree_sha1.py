from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from projectkoios.frankensteins.evidence import directory_git_tree_sha1


class DirectoryGitTreeSha1Test(unittest.TestCase):
    def test_matches_git_for_nested_regular_files_and_executable_modes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(
                ("git", "-C", str(repository), "init", "--quiet"),
                check=True,
            )
            (repository / "fixture/nested").mkdir(parents=True)
            (repository / "fixture/data.txt").write_bytes(b"data\n")
            executable = repository / "fixture/nested/run.sh"
            executable.write_bytes(b"#!/bin/sh\n")
            executable.chmod(0o755)
            subprocess.run(
                ("git", "-C", str(repository), "add", "fixture"),
                check=True,
            )
            root_tree = subprocess.run(
                ("git", "-C", str(repository), "write-tree"),
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            expected = subprocess.run(
                ("git", "-C", str(repository), "rev-parse", f"{root_tree}:fixture"),
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

            observed = directory_git_tree_sha1(
                repository,
                "fixture",
                maximum_files=2,
                maximum_file_bytes=100,
                label="fixture tree",
            )

            self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
