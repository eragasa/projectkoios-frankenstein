from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

from projectkoios.frankensteins.engines.pyflamestk_lmps_mgo_serial_uniform import (
    constants as pyflamestk,
)
from projectkoios.frankensteins.integrations.lammps.provenance import (
    PYPOSPACK_LICENSE_PATH,
    PYPOSPACK_LICENSE_SHA256,
    PYPOSPACK_REPOSITORY_URL,
    PYPOSPACK_REVISION,
    PYPOSPACK_TREE,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class SourceReferencesTest(unittest.TestCase):
    def test_pyflamestk_reference_matches_implementation_binding(self) -> None:
        reference = tomllib.loads(
            (REPOSITORY_ROOT / "sources/pyflamestk.toml").read_text(encoding="utf-8")
        )
        self.assertEqual(reference["repository"], pyflamestk.SOURCE_REPOSITORY_URL)
        self.assertEqual(reference["revision"], pyflamestk.SOURCE_REVISION)
        self.assertEqual(reference["tree"], pyflamestk.SOURCE_TREE)
        self.assertEqual(reference["license_path"], pyflamestk.SOURCE_LICENSE_PATH)
        self.assertEqual(
            reference["license_sha256"],
            pyflamestk.SOURCE_LICENSE_SHA256,
        )

    def test_pypospack_reference_matches_implementation_binding(self) -> None:
        reference = tomllib.loads(
            (REPOSITORY_ROOT / "sources/pypospack.toml").read_text(encoding="utf-8")
        )
        self.assertEqual(reference["repository"], PYPOSPACK_REPOSITORY_URL)
        self.assertEqual(reference["revision"], PYPOSPACK_REVISION)
        self.assertEqual(reference["tree"], PYPOSPACK_TREE)
        self.assertEqual(reference["license_path"], PYPOSPACK_LICENSE_PATH)
        self.assertEqual(reference["license_sha256"], PYPOSPACK_LICENSE_SHA256)

    def test_source_references_are_metadata_only(self) -> None:
        source_entries = tuple(sorted(REPOSITORY_ROOT.joinpath("sources").iterdir()))
        self.assertEqual(
            tuple(path.name for path in source_entries),
            ("pyflamestk.toml", "pypospack.toml"),
        )
        self.assertTrue(all(path.is_file() for path in source_entries))


if __name__ == "__main__":
    unittest.main()
