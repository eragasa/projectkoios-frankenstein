from __future__ import annotations

import re
import unittest

from tests.support.repository_root import REPOSITORY_ROOT

_TASK_ROOT = REPOSITORY_ROOT / "tasks"
_SLICE_ROOT = REPOSITORY_ROOT / "slices"
_MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_REQUIRED_MODULE_ROOTS = (
    _TASK_ROOT / "qe",
    _TASK_ROOT / "workflow" / "qe",
    _TASK_ROOT / "wannier",
    _TASK_ROOT / "workflow" / "wannier",
)


class PlanningHierarchyTest(unittest.TestCase):
    def test__task_index__points_to_disposition_pages(self) -> None:
        text = (_TASK_ROOT / "index.md").read_text(encoding="utf-8")

        for name in ("active.md", "deferred.md", "closed.md"):
            with self.subTest(name=name):
                self.assertIn(f"]({name})", text)
                self.assertTrue((_TASK_ROOT / name).is_file())

    def test__task_hierarchy__contains_required_module_roots(self) -> None:
        for root in _REQUIRED_MODULE_ROOTS:
            with self.subTest(root=root.relative_to(REPOSITORY_ROOT)):
                self.assertTrue((root / "index.md").is_file())

    def test__planning_directories__have_indexes(self) -> None:
        for root in (_TASK_ROOT, _SLICE_ROOT):
            for directory in sorted(path for path in root.rglob("*") if path.is_dir()):
                if directory.name == "subtasks":
                    continue
                with self.subTest(directory=directory.relative_to(REPOSITORY_ROOT)):
                    self.assertTrue((directory / "index.md").is_file())

    def test__slice_pages__declare_consumed_work(self) -> None:
        slice_pages = tuple(
            sorted((_SLICE_ROOT / "bulk-silicon-qe").glob("*/index.md"))
        )
        self.assertTrue(slice_pages)
        for page in slice_pages:
            text = page.read_text(encoding="utf-8")
            with self.subTest(page=page.relative_to(REPOSITORY_ROOT)):
                self.assertTrue(
                    "## Consumed tasks" in text or "## Consumed slices" in text
                )

    def test__planning_links__resolve(self) -> None:
        pages = tuple(sorted((*_TASK_ROOT.rglob("*.md"), *_SLICE_ROOT.rglob("*.md"))))
        self.assertTrue(pages)
        for page in pages:
            text = page.read_text(encoding="utf-8")
            for raw_target in _MARKDOWN_LINK.findall(text):
                target = raw_target.split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                resolved = (page.parent / target).resolve()
                with self.subTest(
                    page=page.relative_to(REPOSITORY_ROOT),
                    target=raw_target,
                ):
                    self.assertTrue(resolved.is_file(), str(resolved))


if __name__ == "__main__":
    unittest.main()
