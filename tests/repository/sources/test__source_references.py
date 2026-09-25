from __future__ import annotations

import tomllib
import unittest

from projectkoios.frankensteins.engines.pyflamestk_lmps_mgo_serial_uniform import (
    constants as pyflamestk,
)
from projectkoios.frankensteins.integrations.lammps.provenance import (
    PYPOSPACK_LICENSE_PATH,
    PYPOSPACK_LICENSE_SHA256,
    PYPOSPACK_RELEASE_TAG,
    PYPOSPACK_REPOSITORY_URL,
    PYPOSPACK_REVISION,
    PYPOSPACK_TREE,
)
from tests.support.repository_root import REPOSITORY_ROOT


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
        self.assertEqual(reference["release_tag"], PYPOSPACK_RELEASE_TAG)
        self.assertEqual(reference["revision"], PYPOSPACK_REVISION)
        self.assertEqual(reference["tree"], PYPOSPACK_TREE)
        self.assertEqual(reference["license_path"], PYPOSPACK_LICENSE_PATH)
        self.assertEqual(reference["license_sha256"], PYPOSPACK_LICENSE_SHA256)

    def test_pymatmc2_reference_is_pinned_without_an_engine_claim(self) -> None:
        reference = tomllib.loads(
            (REPOSITORY_ROOT / "sources/pymatmc2.toml").read_text(encoding="utf-8")
        )
        self.assertEqual(reference["repository"], "https://github.com/eragasa/pymatmc2")
        self.assertEqual(
            reference["revision"],
            "9d31d7fd4f8902f17864fbf391059101a3f5afda",
        )
        self.assertEqual(
            reference["tree"],
            "7773f886eaecfe919abf68d9e4f990fb398a82be",
        )
        self.assertEqual(reference["license_path"], "LICENSE")
        self.assertEqual(
            reference["license_sha256"],
            "2080cab2d2ec5b2a17322121dd1b8ce00d44da7bdfe3e6e01d45316971ca65bd",
        )
        self.assertEqual(reference["selection"]["status"], "reference-only")

    def test_source_references_are_metadata_only(self) -> None:
        source_entries = tuple(sorted(REPOSITORY_ROOT.joinpath("sources").iterdir()))
        self.assertEqual(
            tuple(path.name for path in source_entries),
            ("pyflamestk.toml", "pymatmc2.toml", "pypospack.toml"),
        )
        self.assertTrue(all(path.is_file() for path in source_entries))


if __name__ == "__main__":
    unittest.main()
