from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

from tests.support.repository_root import REPOSITORY_ROOT

SOURCE_ROOT = REPOSITORY_ROOT / "src/projectkoios"
DOCUMENTATION_ROOT = REPOSITORY_ROOT / "docs"
_MARKDOWN_LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
ARCHITECTURE_MODULES = (
    "adapters",
    "calculator-selectable-relaxation",
    "cpn-composition",
    "cpn-visualization",
    "cpn-workflow",
    "historical-pypospack",
    "inverse-problem-forward-evaluation",
    "multi-objective-optimization",
    "potential-optimization",
    "pyflamestk-mgo-examples",
    "qoi-evaluation",
    "reduced-hamiltonian-inverse-problem",
    "simulation-execution",
    "validation",
)


def documentation_path(source: Path) -> Path:
    relative = source.relative_to(REPOSITORY_ROOT / "src")
    if source.name == "__init__.py":
        return DOCUMENTATION_ROOT / relative.parent / "index.md"
    return DOCUMENTATION_ROOT / relative.with_suffix("") / "index.md"


class DocumentationLayoutTest(unittest.TestCase):
    def test_every_maintained_module_and_class_has_mirrored_documentation(self) -> None:
        self.assertTrue((DOCUMENTATION_ROOT / "index.md").is_file())
        modules = tuple(sorted(SOURCE_ROOT.rglob("*.py")))
        self.assertTrue(modules)

        documented_classes = 0
        for source in modules:
            with self.subTest(module=source.relative_to(SOURCE_ROOT)):
                module_documentation = documentation_path(source)
                self.assertTrue(module_documentation.is_file())
                tree = ast.parse(
                    source.read_text(encoding="utf-8"),
                    filename=str(source),
                )
                for node in tree.body:
                    if not isinstance(node, ast.ClassDef):
                        continue
                    class_documentation = (
                        module_documentation.parent / node.name / "index.md"
                    )
                    self.assertTrue(class_documentation.is_file())
                    class_text = class_documentation.read_text(encoding="utf-8")
                    for member in node.body:
                        public_member_names: list[str] = []
                        if isinstance(member, ast.FunctionDef):
                            public_member_names.append(member.name)
                        elif isinstance(member, ast.AnnAssign) and isinstance(
                            member.target, ast.Name
                        ):
                            public_member_names.append(member.target.id)
                        elif isinstance(member, ast.Assign):
                            public_member_names.extend(
                                target.id
                                for target in member.targets
                                if isinstance(target, ast.Name)
                            )
                        for name in public_member_names:
                            if not name.startswith("_"):
                                self.assertIn(name, class_text)
                    documented_classes += 1
        self.assertGreater(documented_classes, 0)

    def test_module_pages_name_every_public_implemented_symbol(self) -> None:
        for source in sorted(SOURCE_ROOT.rglob("*.py")):
            module_documentation = documentation_path(source)
            documentation = module_documentation.read_text(encoding="utf-8")
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
            public_names: list[str] = []
            for node in tree.body:
                if isinstance(node, ast.ClassDef | ast.FunctionDef):
                    if not node.name.startswith("_"):
                        public_names.append(node.name)
                elif isinstance(node, ast.Assign):
                    public_names.extend(
                        target.id
                        for target in node.targets
                        if isinstance(target, ast.Name)
                        and not target.id.startswith("_")
                    )
                elif isinstance(node, ast.AnnAssign):
                    if isinstance(
                        node.target, ast.Name
                    ) and not node.target.id.startswith("_"):
                        public_names.append(node.target.id)
                elif (
                    isinstance(node, ast.TypeAlias)
                    and isinstance(node.name, ast.Name)
                    and not node.name.id.startswith("_")
                ):
                    public_names.append(node.name.id)
            for name in public_names:
                with self.subTest(
                    module=source.relative_to(SOURCE_ROOT),
                    symbol=name,
                ):
                    self.assertIn(name, documentation)

    def test_architecture_modules_have_the_standard_documentation_views(
        self,
    ) -> None:
        architecture_root = DOCUMENTATION_ROOT / "architecture"
        for module_name in ARCHITECTURE_MODULES:
            module_root = architecture_root / module_name
            with self.subTest(module=module_name):
                overview = module_root / "index.md"
                architecture = module_root / "architecture/index.md"
                implementation = module_root / "implementation/index.md"
                specifications = module_root / "specifications/index.md"
                testing = module_root / "testing/index.md"
                for page in (
                    overview,
                    architecture,
                    implementation,
                    specifications,
                    testing,
                ):
                    self.assertTrue(page.is_file(), str(page))

                architecture_text = architecture.read_text(encoding="utf-8")
                self.assertIn("```mermaid", architecture_text)
                self.assertNotIn("classDiagram", architecture_text)
                self.assertNotIn("Proposed package", architecture_text)

                implementation_text = implementation.read_text(encoding="utf-8")
                self.assertIn("```mermaid", implementation_text)
                self.assertIn("classDiagram", implementation_text)

    def test_internal_documentation_links_resolve(self) -> None:
        pages = tuple(sorted(DOCUMENTATION_ROOT.rglob("*.md")))
        self.assertTrue(pages)
        for page in pages:
            text = page.read_text(encoding="utf-8")
            for raw_target in _MARKDOWN_LINK.findall(text):
                target = raw_target.split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                resolved = (page.parent / target).resolve()
                with self.subTest(
                    page=page.relative_to(DOCUMENTATION_ROOT),
                    target=raw_target,
                ):
                    self.assertTrue(resolved.is_file(), str(resolved))
                    self.assertTrue(resolved.is_relative_to(DOCUMENTATION_ROOT))


if __name__ == "__main__":
    unittest.main()
