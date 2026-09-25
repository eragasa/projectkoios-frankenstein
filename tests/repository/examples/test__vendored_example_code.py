from __future__ import annotations

import hashlib
import json
import os
import tomllib
import unittest
from pathlib import Path
from typing import Any

from tests.support.repository_root import REPOSITORY_ROOT

EXAMPLES_ROOT = REPOSITORY_ROOT / "examples"
EXPECTED_CODE_FILE_COUNTS = {
    "pyflamestk": 172,
    "pypospack": 492,
    "pymatmc2": 0,
}


def _git_blob_oid(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()


def _manifest(component: str) -> dict[str, Any]:
    path = EXAMPLES_ROOT / component / "PROVENANCE.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _local_representation_files(component: str) -> set[Path]:
    if component != "pypospack":
        return set()
    component_root = Path("examples") / component
    manifest_path = EXAMPLES_ROOT / component / "MgO/buck/PROVENANCE.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = {Path("MgO/buck/PROVENANCE.json")}
    for collection, field in (
        ("files", "vendored_path"),
        ("derived_files", "vendored_path"),
        ("maintained_files", "path"),
    ):
        result.update(
            Path(record[field]).relative_to(component_root)
            for record in manifest[collection]
        )
    return result


class VendoredExampleCodeTest(unittest.TestCase):
    def test_manifests_match_pinned_source_declarations(self) -> None:
        for component in EXPECTED_CODE_FILE_COUNTS:
            with self.subTest(component=component):
                source = tomllib.loads(
                    REPOSITORY_ROOT.joinpath("sources", f"{component}.toml").read_text(
                        encoding="utf-8"
                    )
                )
                manifest = _manifest(component)
                self.assertEqual(manifest["component"], component)
                self.assertEqual(manifest["repository"], source["repository"])
                self.assertEqual(manifest["revision"], source["revision"])
                self.assertEqual(manifest["tree"], source["tree"])
                self.assertEqual(manifest["upstream_examples_root"], "examples")
                self.assertEqual(
                    manifest["license"]["sha256"], source["license_sha256"]
                )

    def test_every_vendored_file_matches_its_recorded_identity(self) -> None:
        for component, expected_count in EXPECTED_CODE_FILE_COUNTS.items():
            manifest = _manifest(component)
            records = manifest["files"]
            self.assertEqual(len(records), expected_count)
            self.assertEqual(
                [record["original_path"] for record in records],
                sorted(record["original_path"] for record in records),
            )
            for record in records:
                with self.subTest(
                    component=component,
                    original_path=record["original_path"],
                ):
                    self.assertTrue(record["original_path"].startswith("examples/"))
                    expected_path = (
                        Path("examples")
                        / component
                        / Path(record["original_path"]).relative_to("examples")
                    )
                    self.assertEqual(record["vendored_path"], expected_path.as_posix())
                    path = REPOSITORY_ROOT / expected_path
                    data = path.read_bytes()
                    self.assertEqual(len(data), record["byte_size"])
                    self.assertEqual(hashlib.sha256(data).hexdigest(), record["sha256"])
                    self.assertEqual(_git_blob_oid(data), record["git_blob_oid"])
                    executable = bool(path.stat().st_mode & 0o111)
                    self.assertEqual(executable, record["git_mode"] == "100755")

    def test_each_repository_directory_contains_only_declared_code_and_metadata(
        self,
    ) -> None:
        for component in EXPECTED_CODE_FILE_COUNTS:
            manifest = _manifest(component)
            declared = {
                Path(record["vendored_path"]).relative_to(Path("examples") / component)
                for record in manifest["files"]
            }
            declared.update(
                {Path("LICENSE"), Path("PROVENANCE.json"), Path("VENDORING.md")}
            )
            declared.update(_local_representation_files(component))
            observed = {
                path.relative_to(EXAMPLES_ROOT / component)
                for path in (EXAMPLES_ROOT / component).rglob("*")
                if path.is_file()
            }
            with self.subTest(component=component):
                self.assertEqual(observed, declared)

    def test_vendored_licenses_match_their_manifest_identities(self) -> None:
        for component in EXPECTED_CODE_FILE_COUNTS:
            manifest = _manifest(component)
            license_record = manifest["license"]
            path = REPOSITORY_ROOT / license_record["vendored_path"]
            data = path.read_bytes()
            with self.subTest(component=component):
                self.assertEqual(len(data), license_record["byte_size"])
                self.assertEqual(
                    hashlib.sha256(data).hexdigest(), license_record["sha256"]
                )
                self.assertEqual(_git_blob_oid(data), license_record["git_blob_oid"])
                self.assertFalse(bool(path.stat().st_mode & os.X_OK))

    def test_extracted_mgo_buck_files_match_their_source_blobs(self) -> None:
        manifest_path = EXAMPLES_ROOT / "pypospack/MgO/buck/PROVENANCE.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        source = tomllib.loads(
            REPOSITORY_ROOT.joinpath("sources/pypospack.toml").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["repository"], source["repository"])
        self.assertEqual(manifest["revision"], source["revision"])
        self.assertEqual(manifest["tree"], source["tree"])

        self.assertEqual(len(manifest["files"]), 23)
        self.assertEqual(
            sum(record["role"] == "qoi_runtime" for record in manifest["files"]),
            16,
        )
        selected_files = {
            record["path"]: record for record in source["selection"]["additional_files"]
        }
        directly_selected = (
            record
            for record in manifest["files"]
            if record["original_path"] in selected_files
        )
        for record in directly_selected:
            selected = selected_files[record["original_path"]]
            self.assertEqual(record["sha256"], selected["sha256"])
            self.assertEqual(record["byte_size"], selected["byte_size"])

        for record in manifest["files"]:
            with self.subTest(original_path=record["original_path"]):
                self.assertEqual(record["local_modifications"], "None")
                path = REPOSITORY_ROOT / record["vendored_path"]
                data = path.read_bytes()
                self.assertEqual(len(data), record["byte_size"])
                self.assertEqual(hashlib.sha256(data).hexdigest(), record["sha256"])
                self.assertEqual(_git_blob_oid(data), record["git_blob_oid"])

    def test_mgo_buck_sampler_has_documented_local_modifications(self) -> None:
        manifest_path = EXAMPLES_ROOT / "pypospack/MgO/buck/PROVENANCE.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["derived_files"]), 2)
        for derived_record in manifest["derived_files"]:
            with self.subTest(role=derived_record["role"]):
                data = REPOSITORY_ROOT.joinpath(
                    derived_record["vendored_path"]
                ).read_bytes()
                self.assertEqual(len(data), derived_record["byte_size"])
                self.assertEqual(
                    hashlib.sha256(data).hexdigest(), derived_record["sha256"]
                )
                self.assertTrue(derived_record["local_modifications"])

        record = next(
            item
            for item in manifest["derived_files"]
            if item["role"] == "iterative_sampler_entrypoint"
        )

        original = EXAMPLES_ROOT / "pypospack/MgO__buck__iterative_sampler"
        original_data = original.joinpath("mc_iterative_sampler.py").read_bytes()
        self.assertEqual(_git_blob_oid(original_data), record["based_on_git_blob_oid"])
        self.assertEqual(
            hashlib.sha256(original_data).hexdigest(), record["based_on_sha256"]
        )

        derived_data = REPOSITORY_ROOT.joinpath(record["vendored_path"]).read_bytes()
        self.assertEqual(len(derived_data), record["byte_size"])
        self.assertEqual(hashlib.sha256(derived_data).hexdigest(), record["sha256"])
        derived_text = derived_data.decode("utf-8")
        self.assertIn(
            "from mc_sampler_iterate import PyposmatIterativeSampler", derived_text
        )
        self.assertIn("MgOBuckinghamConfiguration.from_legacy_file", derived_text)
        self.assertIn("execution.validate(require_lammps=True)", derived_text)
        self.assertIn("write_resolved_snapshot", derived_text)
        self.assertIn("sampler.rv_seed = random_seed", derived_text)
        self.assertTrue(record["local_modifications"])

    def test_mgo_buck_maintained_files_match_their_manifest_identities(self) -> None:
        manifest_path = EXAMPLES_ROOT / "pypospack/MgO/buck/PROVENANCE.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["maintained_files"]), 3)
        for record in manifest["maintained_files"]:
            with self.subTest(path=record["path"]):
                data = REPOSITORY_ROOT.joinpath(record["path"]).read_bytes()
                self.assertEqual(len(data), record["byte_size"])
                self.assertEqual(hashlib.sha256(data).hexdigest(), record["sha256"])
                self.assertIn("Locally authored", record["origin"])


if __name__ == "__main__":
    unittest.main()
