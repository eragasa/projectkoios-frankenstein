from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from projectkoios.frankensteins.integrations.lammps import (
    PYPOSPACK_LAMMPS_BYTE_SIZE,
    PYPOSPACK_LAMMPS_LIMITATIONS,
    PYPOSPACK_LAMMPS_PATH,
    PYPOSPACK_LAMMPS_SHA256,
    PYPOSPACK_LICENSE_SHA256,
    PYPOSPACK_REPOSITORY_URL,
    PYPOSPACK_REVISION,
    PYPOSPACK_TREE,
    LammpsAtom,
    LammpsSimulationCell,
    PypospackLammpsProvenance,
    render_lammps_data,
    verify_pypospack_lammps_checkout,
)
from projectkoios.frankensteins.integrations.lammps.provenance import (
    PYPOSPACK_LICENSE_PATH,
)

_CHECKOUT_VALUE = os.environ.get("PYPOSPACK_CHECKOUT")
CHECKOUT = Path(_CHECKOUT_VALUE).resolve() if _CHECKOUT_VALUE else None


def bound_source() -> PypospackLammpsProvenance:
    return PypospackLammpsProvenance(
        component="pypospack",
        repository_url=PYPOSPACK_REPOSITORY_URL,
        revision=PYPOSPACK_REVISION,
        tree=PYPOSPACK_TREE,
        source_path=PYPOSPACK_LAMMPS_PATH,
        source_sha256=PYPOSPACK_LAMMPS_SHA256,
        source_byte_size=PYPOSPACK_LAMMPS_BYTE_SIZE,
        license_path=PYPOSPACK_LICENSE_PATH,
        license_sha256=PYPOSPACK_LICENSE_SHA256,
        source_limitations=PYPOSPACK_LAMMPS_LIMITATIONS,
    )


class LammpsDataReconstructionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.source = bound_source()
        self.cell = LammpsSimulationCell(
            scale=2.0,
            lattice=(
                (1.0, 0.0, 0.0),
                (0.0, 2.0, 0.0),
                (0.0, 0.0, 3.0),
            ),
            atoms=(
                LammpsAtom("O", (0.5, 0.5, 0.5), charge=-2.0),
                LammpsAtom("Mg", (0.0, 0.0, 0.0), charge=2.0),
            ),
        )

    def test_provenance_contract_is_exact_and_immutable(self) -> None:
        self.assertEqual(self.source.component, "pypospack")
        self.assertEqual(self.source.revision, PYPOSPACK_REVISION)
        self.assertEqual(self.source.source_path, PYPOSPACK_LAMMPS_PATH)
        self.assertEqual(self.source.source_byte_size, 3_030)
        self.assertTrue(self.source.source_limitations)

        with self.assertRaisesRegex(ValueError, "source size"):
            replace(self.source, source_byte_size=3_031)
        with self.assertRaisesRegex(ValueError, "limitations"):
            replace(self.source, source_limitations=("invented",))

    def test_renders_stable_effect_free_charge_data(self) -> None:
        first = render_lammps_data(
            cell=self.cell,
            species_order=("Mg", "O"),
            atom_style="charge",
            source=self.source,
        )
        second = render_lammps_data(
            cell=self.cell,
            species_order=("Mg", "O"),
            atom_style="charge",
            source=self.source,
        )

        self.assertEqual(first, second)
        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(
            first.utf8_text,
            "# ['Mg', 'O']\n"
            "\n"
            "2 atoms\n"
            "2 atom types\n"
            "\n"
            "    0.0000     2.0000 xlo xhi\n"
            "    0.0000     4.0000 ylo yhi\n"
            "    0.0000     6.0000 zlo zhi\n"
            "\n"
            "    0.0000     0.0000     0.0000 xy xz yz\n"
            "\n"
            "Atoms\n"
            "\n"
            "1 1     2.0000     0.0000     0.0000     0.0000\n"
            "2 2    -2.0000     1.0000     2.0000     3.0000\n",
        )
        payload = first.to_dict()
        self.assertEqual(
            payload["contract"],
            "projectkoios.frankensteins.integrations.lammps-data",
        )
        self.assertFalse(payload["calculator_execution_authorized"])
        self.assertFalse(payload["scientific_validation_claimed"])
        self.assertNotIn("utf8_text", payload)
        self.assertEqual(first.to_dict(include_text=True)["utf8_text"], first.utf8_text)

    def test_rejects_unsupported_or_numerically_unsafe_cells(self) -> None:
        triclinic = replace(
            self.cell,
            lattice=(
                (1.0, 0.25, 0.0),
                (0.0, 2.0, 0.0),
                (0.0, 0.0, 3.0),
            ),
        )
        with self.assertRaisesRegex(ValueError, "off-diagonal"):
            render_lammps_data(
                cell=triclinic,
                species_order=("Mg", "O"),
                atom_style="atomic",
                source=self.source,
            )

        overflowing = LammpsSimulationCell(
            scale=1e308,
            lattice=(
                (2.0, 0.0, 0.0),
                (0.0, 2.0, 0.0),
                (0.0, 0.0, 2.0),
            ),
            atoms=(LammpsAtom("Mg", (0.0, 0.0, 0.0)),),
        )
        with self.assertRaisesRegex(ValueError, "finite and positive"):
            render_lammps_data(
                cell=overflowing,
                species_order=("Mg",),
                atom_style="atomic",
                source=self.source,
            )

    def test_rejects_missing_charges_and_incomplete_species_order(self) -> None:
        without_charges = replace(
            self.cell,
            atoms=(LammpsAtom("Mg", (0.0, 0.0, 0.0)),),
        )
        with self.assertRaisesRegex(ValueError, "explicit charge"):
            render_lammps_data(
                cell=without_charges,
                species_order=("Mg",),
                atom_style="charge",
                source=self.source,
            )
        with self.assertRaisesRegex(ValueError, "exactly cover"):
            render_lammps_data(
                cell=self.cell,
                species_order=("Mg",),
                atom_style="atomic",
                source=self.source,
            )

    @unittest.skipUnless(CHECKOUT is not None, "PYPOSPACK_CHECKOUT is not set")
    def test_verifies_explicit_external_checkout(self) -> None:
        assert CHECKOUT is not None
        self.assertEqual(verify_pypospack_lammps_checkout(CHECKOUT), self.source)

    @unittest.skipUnless(CHECKOUT is not None, "PYPOSPACK_CHECKOUT is not set")
    def test_detects_mutated_or_symlinked_source_evidence(self) -> None:
        assert CHECKOUT is not None
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory)
            for relative_path in (PYPOSPACK_LICENSE_PATH, PYPOSPACK_LAMMPS_PATH):
                destination = checkout / relative_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(CHECKOUT / relative_path, destination)

            source_path = checkout / PYPOSPACK_LAMMPS_PATH
            source_path.write_bytes(source_path.read_bytes() + b"\n# mutation\n")
            with self.assertRaisesRegex(ValueError, "bound source"):
                verify_pypospack_lammps_checkout(checkout)

            source_path.unlink()
            source_path.symlink_to(CHECKOUT / PYPOSPACK_LAMMPS_PATH)
            with self.assertRaisesRegex(ValueError, "regular file"):
                verify_pypospack_lammps_checkout(checkout)


if __name__ == "__main__":
    unittest.main()
