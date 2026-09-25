from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from projectkoios.frankensteins.evidence import list_regular_files


class ListRegularFilesTest(unittest.TestCase):
    def test_lists_sorted_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tree/nested").mkdir(parents=True)
            (root / "tree/z.txt").write_bytes(b"z")
            (root / "tree/nested/a.txt").write_bytes(b"evidence")

            self.assertEqual(
                list_regular_files(
                    root,
                    "tree",
                    maximum_files=2,
                    label="fixture tree",
                ),
                ("nested/a.txt", "z.txt"),
            )

    def test_rejects_symbolic_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tree").mkdir()
            (root / "tree/evidence.txt").write_bytes(b"evidence")
            (root / "tree/linked-file").symlink_to(root / "tree/evidence.txt")

            with self.assertRaisesRegex(ValueError, "symbolic link"):
                list_regular_files(
                    root,
                    "tree",
                    maximum_files=10,
                    label="fixture tree",
                )

    def test_rejects_a_tree_above_the_file_count_bound(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tree").mkdir()
            (root / "tree/evidence.txt").write_bytes(b"evidence")
            (root / "tree/other.txt").write_bytes(b"other")

            with self.assertRaisesRegex(ValueError, "file-count bound"):
                list_regular_files(
                    root,
                    "tree",
                    maximum_files=1,
                    label="fixture tree",
                )


if __name__ == "__main__":
    unittest.main()
