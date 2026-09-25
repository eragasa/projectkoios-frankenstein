from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.normalize_markdown import (
    MarkdownNormalizationRequest,
    MarkdownNormalizer,
)


class MarkdownNormalizerTest(unittest.TestCase):
    def test_check_reports_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "document.md"
            source = "wrapped prose on the first\nsource line continues here.\n"
            path.write_text(source, encoding="utf-8")

            result = MarkdownNormalizer().actionize(
                MarkdownNormalizationRequest(paths=(path,), operation="check")
            )

            self.assertEqual(result.changed_count, 1)
            self.assertTrue(result.records[0].changed)
            self.assertEqual(path.read_text(encoding="utf-8"), source)

    def test_write_normalizes_recursively_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            path = root / "nested/document.md"
            path.parent.mkdir()
            path.write_text(
                "wrapped prose on the first\nline continues.\n", encoding="utf-8"
            )

            first = MarkdownNormalizer().actionize(
                MarkdownNormalizationRequest(paths=(root,), operation="write")
            )
            second = MarkdownNormalizer().actionize(
                MarkdownNormalizationRequest(paths=(root,), operation="check")
            )

            self.assertEqual(first.changed_count, 1)
            self.assertEqual(second.changed_count, 0)
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                "wrapped prose on the first line continues.\n",
            )

    def test_rejects_symbolic_link_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            target = root / "target.md"
            target.write_text("text\n", encoding="utf-8")
            link = root / "link.md"
            link.symlink_to(target)

            with self.assertRaisesRegex(ValueError, "symbolic links"):
                MarkdownNormalizer().actionize(
                    MarkdownNormalizationRequest(paths=(link,), operation="check")
                )


if __name__ == "__main__":
    unittest.main()
