from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import projectkoios.frankensteins.evidence as evidence_module
from projectkoios.frankensteins.evidence import (
    list_regular_files,
    read_bounded_regular_file,
)


class EvidenceTest(unittest.TestCase):
    def test_reads_a_bounded_regular_file_and_lists_sorted_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tree/nested").mkdir(parents=True)
            (root / "tree/z.txt").write_bytes(b"z")
            (root / "tree/nested/a.txt").write_bytes(b"evidence")

            self.assertEqual(
                read_bounded_regular_file(
                    root,
                    "tree/nested/a.txt",
                    maximum_bytes=8,
                    label="fixture evidence",
                ),
                b"evidence",
            )
            self.assertEqual(
                list_regular_files(
                    root,
                    "tree",
                    maximum_files=2,
                    label="fixture tree",
                ),
                ("nested/a.txt", "z.txt"),
            )

    def test_rejects_final_and_ancestor_symbolic_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "actual").mkdir()
            (root / "actual/evidence.txt").write_bytes(b"evidence")
            (root / "actual/linked-file").symlink_to(root / "actual/evidence.txt")
            (root / "linked-file").symlink_to(root / "actual/evidence.txt")
            (root / "linked-directory").symlink_to(root / "actual")

            with self.assertRaisesRegex(ValueError, "safely readable"):
                read_bounded_regular_file(
                    root,
                    "linked-file",
                    maximum_bytes=100,
                    label="linked evidence",
                )
            with self.assertRaisesRegex(ValueError, "safely readable"):
                read_bounded_regular_file(
                    root,
                    "linked-directory/evidence.txt",
                    maximum_bytes=100,
                    label="linked evidence",
                )
            with self.assertRaisesRegex(ValueError, "safely readable"):
                read_bounded_regular_file(
                    root / "linked-directory",
                    "evidence.txt",
                    maximum_bytes=100,
                    label="linked root evidence",
                )
            with self.assertRaisesRegex(ValueError, "symbolic link"):
                list_regular_files(
                    root,
                    "actual",
                    maximum_files=10,
                    label="fixture tree",
                )

    def test_rejects_a_symbolic_link_swap_before_the_file_open(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "evidence.txt"
            replacement = root / "replacement.txt"
            target.write_bytes(b"original")
            replacement.write_bytes(b"replacement")
            original_open = evidence_module._open_child_file
            swapped = False

            def swapping_open(parent: int, name: str, label: str) -> int:
                nonlocal swapped
                if not swapped:
                    swapped = True
                    target.unlink()
                    target.symlink_to(replacement)
                return original_open(parent, name, label)

            with (
                patch.object(evidence_module, "_open_child_file", swapping_open),
                self.assertRaisesRegex(ValueError, "safely readable"),
            ):
                read_bounded_regular_file(
                    root,
                    "evidence.txt",
                    maximum_bytes=100,
                    label="swapped evidence",
                )

    def test_rejects_oversized_and_escaping_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tree").mkdir()
            (root / "tree/evidence.txt").write_bytes(b"too large")
            (root / "tree/other.txt").write_bytes(b"other")

            with self.assertRaisesRegex(ValueError, "byte bound"):
                read_bounded_regular_file(
                    root,
                    "tree/evidence.txt",
                    maximum_bytes=3,
                    label="fixture evidence",
                )
            with self.assertRaisesRegex(ValueError, "normalized relative path"):
                read_bounded_regular_file(
                    root,
                    "../evidence.txt",
                    maximum_bytes=100,
                    label="fixture evidence",
                )
            with self.assertRaisesRegex(ValueError, "file-count bound"):
                list_regular_files(
                    root,
                    "tree",
                    maximum_files=1,
                    label="fixture tree",
                )

    def test_detects_mutation_during_a_file_read(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "evidence.txt"
            target.write_bytes(b"before")
            original_read = os.read
            mutated = False

            def mutating_read(descriptor: int, size: int) -> bytes:
                nonlocal mutated
                chunk = original_read(descriptor, size)
                if chunk and not mutated:
                    mutated = True
                    target.write_bytes(b"changed after descriptor read")
                return chunk

            with (
                patch("projectkoios.frankensteins.evidence.os.read", mutating_read),
                self.assertRaisesRegex(ValueError, "changed during read"),
            ):
                read_bounded_regular_file(
                    root,
                    "evidence.txt",
                    maximum_bytes=100,
                    label="mutable evidence",
                )


if __name__ == "__main__":
    unittest.main()
