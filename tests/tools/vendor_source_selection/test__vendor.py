from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

from tests.support.repository_root import REPOSITORY_ROOT

TOOL_PATH = REPOSITORY_ROOT / "tools/vendor_source_selection.py"


def _load_tool() -> ModuleType:
    module_name = "projectkoios_vendor_source_selection"
    spec = importlib.util.spec_from_file_location(module_name, TOOL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load vendoring tool")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    previous_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous_dont_write_bytecode
    return module


tool = _load_tool()
VendoringError = tool.VendoringError


def _git(repository: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(repository), *arguments),
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


class VendorSourceSelectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        root = Path(self.temporary_directory.name)
        self.project = root / "project"
        self.checkout = root / "checkout"
        self.project.mkdir()
        self.checkout.mkdir()

        _git(self.checkout, "init", "-q")
        _git(self.checkout, "config", "user.name", "Test")
        _git(self.checkout, "config", "user.email", "test@example.invalid")
        _git(
            self.checkout,
            "remote",
            "add",
            "origin",
            "https://example.invalid/upstream.git",
        )
        source_file = self.checkout / "package/qoi.py"
        source_file.parent.mkdir()
        source_file.write_bytes(b"VALUE = 1\n")
        unselected = self.checkout / "package/unselected.py"
        unselected.write_bytes(b"VALUE = 2\n")
        license_payload = b"test license\n"
        (self.checkout / "LICENSE").write_bytes(license_payload)
        self.license_sha256 = hashlib.sha256(license_payload).hexdigest()
        _git(self.checkout, "add", ".")
        _git(self.checkout, "commit", "-qm", "source")
        self.revision = _git(self.checkout, "rev-parse", "HEAD")
        self.tree = _git(self.checkout, "rev-parse", "HEAD^{tree}")
        self.package_tree = _git(self.checkout, "rev-parse", "HEAD:package")
        self.payload = source_file.read_bytes()

        sources = self.project / "sources"
        sources.mkdir()
        (sources / "example.toml").write_text(
            "\n".join(
                (
                    "schema_version = 1",
                    'component = "example"',
                    'repository = "https://example.invalid/upstream"',
                    'release_tag = "v1"',
                    f'revision = "{self.revision}"',
                    f'tree = "{self.tree}"',
                    'license_path = "LICENSE"',
                    f'license_sha256 = "{self.license_sha256}"',
                    "",
                    "[selection]",
                    'source_path = "package/qoi.py"',
                    f'source_sha256 = "{hashlib.sha256(self.payload).hexdigest()}"',
                    f"source_byte_size = {len(self.payload)}",
                    "",
                )
            ),
            encoding="utf-8",
        )
        self.recipe = self.project / "recipe.toml"
        self.recipe.write_text(
            "\n".join(
                (
                    "schema_version = 1",
                    'component = "example"',
                    "",
                    "[provenance]",
                    'path = "vendor/PROVENANCE.json"',
                    'source_example = "examples/workflow"',
                    'representation = "test"',
                    "",
                    "[[files]]",
                    'role = "qoi_runtime"',
                    'source = "package/qoi.py"',
                    'destination = "vendor/package/qoi.py"',
                    "",
                )
            ),
            encoding="utf-8",
        )

    def test_sync_extracts_committed_blob_and_writes_provenance(self) -> None:
        tool.vendor(
            repository_root=self.project,
            recipe_path=self.recipe,
            checkout=self.checkout,
            sync=True,
        )

        destination = self.project / "vendor/package/qoi.py"
        self.assertEqual(destination.read_bytes(), self.payload)
        provenance = json.loads(
            self.project.joinpath("vendor/PROVENANCE.json").read_text(encoding="utf-8")
        )
        record = provenance["files"][0]
        self.assertEqual(record["original_path"], "package/qoi.py")
        self.assertEqual(record["sha256"], hashlib.sha256(self.payload).hexdigest())
        self.assertEqual(record["git_mode"], "100644")
        self.assertEqual(provenance["revision"], self.revision)

        tool.vendor(
            repository_root=self.project,
            recipe_path=self.recipe,
            checkout=self.checkout,
            sync=False,
        )

    def test_check_detects_a_modified_destination(self) -> None:
        tool.vendor(
            repository_root=self.project,
            recipe_path=self.recipe,
            checkout=self.checkout,
            sync=True,
        )
        self.project.joinpath("vendor/package/qoi.py").write_text(
            "modified\n", encoding="utf-8"
        )

        with self.assertRaisesRegex(VendoringError, "out of date"):
            tool.vendor(
                repository_root=self.project,
                recipe_path=self.recipe,
                checkout=self.checkout,
                sync=False,
            )

    def test_rejects_a_source_path_not_authorized_by_the_declaration(self) -> None:
        recipe = self.recipe.read_text(encoding="utf-8").replace(
            "package/qoi.py", "package/unselected.py"
        )
        self.recipe.write_text(recipe, encoding="utf-8")

        with self.assertRaisesRegex(VendoringError, "not authorized"):
            tool.vendor(
                repository_root=self.project,
                recipe_path=self.recipe,
                checkout=self.checkout,
                sync=True,
            )

    def test_inline_example_tree_authorizes_a_contained_source_path(self) -> None:
        source_declaration = self.project.joinpath("sources/example.toml").read_text(
            encoding="utf-8"
        )
        self.project.joinpath("sources/example.toml").write_text(
            source_declaration
            + "[selection.example_trees]\n"
            + f'"package" = "{self.package_tree}"\n',
            encoding="utf-8",
        )
        recipe = self.recipe.read_text(encoding="utf-8").replace(
            "package/qoi.py", "package/unselected.py"
        )
        self.recipe.write_text(recipe, encoding="utf-8")

        tool.vendor(
            repository_root=self.project,
            recipe_path=self.recipe,
            checkout=self.checkout,
            sync=True,
        )

        self.assertEqual(
            self.project.joinpath("vendor/package/unselected.py").read_bytes(),
            b"VALUE = 2\n",
        )

    def test_rejects_destination_path_traversal(self) -> None:
        recipe = self.recipe.read_text(encoding="utf-8").replace(
            "vendor/package/qoi.py", "../outside.py"
        )
        self.recipe.write_text(recipe, encoding="utf-8")

        with self.assertRaisesRegex(VendoringError, "normalized relative"):
            tool.load_recipe(self.recipe)


if __name__ == "__main__":
    unittest.main()
