from __future__ import annotations

import hashlib
import json
import unittest

from tests.support.repository_root import REPOSITORY_ROOT

VENDOR_ROOT = REPOSITORY_ROOT / "vendor/pypospack"
EXPECTED_REVISION = "be453fa7191e55a0426f66e8b5b5b0b103c8b29d"
EXPECTED_TREE = "7ac9c9f255aa7731f39ce35a0e561fc113082a6f"
EXPECTED_FILES = {
    "LICENSE": (
        "05f25c4caf59b20bbcadbb1e3e1c33b154d273ef7daa7e7740bca8a0ed0f4c83",
        4550,
    ),
    "pypospack/io/vasp/__init__.py": (
        "125c8ac3ddd402dae197903ce4f33bcfbcc7d587186d0b694700458e6c1b2c0e",
        43581,
    ),
    "pypospack/io/vasp/simulation.py": (
        "420062a314d7dead96a1b6c0eebf1ff0b5fe6f1c5f7559bcf4c0ff7327a5cd26",
        2667,
    ),
    "pypospack/task/vasp.py": (
        "3dbcb3b5d8bc13e834a2580654afdb1bdd26f589b9241374cc5a3663660378db",
        42492,
    ),
    "pypospack/workflows/vasp/kpoint_convergence.py": (
        "c54fe010b774b778542a1fd400bef7a26e86f079d56b5661cd6edbc9a75168b9",
        786,
    ),
}


class VendoredPypospackVaspTest(unittest.TestCase):
    def test_manifest_and_vendored_bytes_match_the_pinned_source(self) -> None:
        manifest = json.loads((VENDOR_ROOT / "PROVENANCE.json").read_text())

        self.assertEqual(manifest["revision"], EXPECTED_REVISION)
        self.assertEqual(manifest["tree"], EXPECTED_TREE)
        records = {record["original_path"]: record for record in manifest["files"]}
        self.assertEqual(set(records), set(EXPECTED_FILES))

        for source_path, (expected_sha256, expected_size) in EXPECTED_FILES.items():
            with self.subTest(source_path=source_path):
                record = records[source_path]
                payload = (REPOSITORY_ROOT / record["vendored_path"]).read_bytes()
                self.assertEqual(len(payload), expected_size)
                self.assertEqual(hashlib.sha256(payload).hexdigest(), expected_sha256)
                self.assertEqual(record["sha256"], expected_sha256)
                self.assertEqual(record["byte_size"], expected_size)
                self.assertEqual(record["local_modifications"], "None")


if __name__ == "__main__":
    unittest.main()
