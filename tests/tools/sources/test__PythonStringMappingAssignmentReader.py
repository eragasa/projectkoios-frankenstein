from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.sources.python_literal_assignment import (
    PythonLiteralAssignmentError,
    PythonStringMappingAssignmentReader,
    PythonStringMappingAssignmentRequest,
)


class PythonStringMappingAssignmentReaderTest(unittest.TestCase):
    def test_reads_an_annotated_literal_without_executing_the_module(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "bindings.py"
            source_path.write_text(
                """\
raise RuntimeError("this module must not execute")
SOURCE_EXAMPLE_TREES: dict[str, str] = {
    "examples/second": "tree-2",
    "examples/first": "tree-1",
}
""",
                encoding="utf-8",
            )
            request = PythonStringMappingAssignmentRequest(
                source_path=source_path,
                assignment_name="SOURCE_EXAMPLE_TREES",
            )

            result = PythonStringMappingAssignmentReader().actionize(request)

            self.assertIs(result.request, request)
            self.assertEqual(
                tuple((entry.key, entry.value) for entry in result.entries),
                (
                    ("examples/second", "tree-2"),
                    ("examples/first", "tree-1"),
                ),
            )

    def test_rejects_duplicate_mapping_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "bindings.py"
            source_path.write_text(
                'VALUE = {"duplicate": "first", "duplicate": "second"}\n',
                encoding="utf-8",
            )
            request = PythonStringMappingAssignmentRequest(
                source_path=source_path,
                assignment_name="VALUE",
            )

            with self.assertRaisesRegex(
                PythonLiteralAssignmentError,
                "duplicate mapping key",
            ):
                PythonStringMappingAssignmentReader().actionize(request)

    def test_rejects_expressions_instead_of_string_literals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "bindings.py"
            source_path.write_text(
                'VALUE = {"path": build_identity()}\n',
                encoding="utf-8",
            )
            request = PythonStringMappingAssignmentRequest(
                source_path=source_path,
                assignment_name="VALUE",
            )

            with self.assertRaisesRegex(
                PythonLiteralAssignmentError,
                "must be a string literal",
            ):
                PythonStringMappingAssignmentReader().actionize(request)

    def test_rejects_a_missing_assignment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "bindings.py"
            source_path.write_text("OTHER = {}\n", encoding="utf-8")
            request = PythonStringMappingAssignmentRequest(
                source_path=source_path,
                assignment_name="VALUE",
            )

            with self.assertRaisesRegex(PythonLiteralAssignmentError, "missing"):
                PythonStringMappingAssignmentReader().actionize(request)


if __name__ == "__main__":
    unittest.main()
