from __future__ import annotations

import json
import unittest

import numpy as np
from physkit.periodic import DirectLattice3D
from physkit.units import PhysicalUnit, ScalarQuantity, Unitless, VectorQuantity

from projectkoios.frankensteins.physkit.periodic.unit_cell import (
    Atom,
    AtomicBasis,
    ConventionalUnitCell,
    PrimitiveUnitCell,
    UnitCell,
    UnitCellJsonDeserializer,
    UnitCellJsonSerializer,
)


class UnitCellTest(unittest.TestCase):
    def test_composes_direct_lattice_scale_and_atomic_basis(self) -> None:
        lattice = _fcc_direct_lattice()
        basis = _silicon_basis()
        lattice_parameter = ScalarQuantity(5.43, PhysicalUnit("angstrom"))

        cell = UnitCell(
            direct_lattice=lattice,
            lattice_parameter=lattice_parameter,
            atomic_basis=basis,
        )

        self.assertIsNot(cell.direct_lattice, lattice)
        np.testing.assert_array_equal(cell.A.magnitude, lattice.A)
        self.assertIs(cell.lattice_parameter, lattice_parameter)
        self.assertIs(cell.atomic_basis, basis)

    def test_exposes_A_and_H_with_vectors_as_columns(self) -> None:
        cell = UnitCell(
            direct_lattice=DirectLattice3D(
                a1=np.array([1.0, 0.0, 0.0]),
                a2=np.array([0.2, 2.0, 0.0]),
                a3=np.array([0.3, 0.4, 3.0]),
            ),
            lattice_parameter=ScalarQuantity(2.0, PhysicalUnit("angstrom")),
            atomic_basis=_silicon_basis(),
        )

        expected_a = np.array(
            (
                (1.0, 0.2, 0.3),
                (0.0, 2.0, 0.4),
                (0.0, 0.0, 3.0),
            )
        )
        np.testing.assert_array_equal(cell.A.magnitude, expected_a)
        np.testing.assert_array_equal(cell.H.magnitude, 2.0 * expected_a)
        np.testing.assert_array_equal(cell.a2.magnitude, expected_a[:, 1])
        np.testing.assert_array_equal(cell.h2.magnitude, 2.0 * expected_a[:, 1])
        self.assertIsInstance(cell.A.unit, Unitless)
        self.assertEqual(cell.H.unit.expression, "angstrom")

    def test_copies_and_freezes_the_direct_lattice_representation(self) -> None:
        source = _fcc_direct_lattice()
        cell = UnitCell(
            direct_lattice=source,
            lattice_parameter=ScalarQuantity(5.43, PhysicalUnit("angstrom")),
            atomic_basis=_silicon_basis(),
        )

        source.A[0, 0] = 99.0

        self.assertEqual(cell.A.magnitude[0, 0], 0.5)
        with self.assertRaises(ValueError):
            cell.direct_lattice.A[0, 0] = 99.0
        with self.assertRaises(ValueError):
            cell.H.magnitude[0, 0] = 99.0

    def test_accepts_lattice_parameter_in_any_physical_length_unit(self) -> None:
        cell = UnitCell(
            direct_lattice=_fcc_direct_lattice(),
            lattice_parameter=ScalarQuantity(10.26121286, PhysicalUnit("bohr")),
            atomic_basis=_silicon_basis(),
        )

        self.assertEqual(cell.lattice_parameter.unit.expression, "bohr")

    def test_rejects_non_length_lattice_parameter(self) -> None:
        with self.assertRaisesRegex(ValueError, "length dimensionality"):
            UnitCell(
                direct_lattice=_fcc_direct_lattice(),
                lattice_parameter=ScalarQuantity(5.43, PhysicalUnit("electron_volt")),
                atomic_basis=_silicon_basis(),
            )

    def test_json_round_trip_preserves_the_primitive_nominal_type(self) -> None:
        cell = PrimitiveUnitCell(
            direct_lattice=_fcc_direct_lattice(),
            lattice_parameter=ScalarQuantity(5.43, PhysicalUnit("angstrom")),
            atomic_basis=_silicon_basis(),
        )

        serialized = UnitCellJsonSerializer().serialize(
            cell,
            structure_id="Si.PrimitiveUnitCell",
        )
        restored = UnitCellJsonDeserializer().deserialize(
            serialized,
            expected_structure_id="Si.PrimitiveUnitCell",
        )

        self.assertIsInstance(restored, PrimitiveUnitCell)
        np.testing.assert_array_equal(restored.A.magnitude, cell.A.magnitude)
        np.testing.assert_array_equal(restored.H.magnitude, cell.H.magnitude)
        self.assertEqual(
            json.loads(serialized)["representation"],
            "primitive",
        )

    def test_json_round_trip_preserves_the_conventional_nominal_type(self) -> None:
        cell = ConventionalUnitCell(
            direct_lattice=DirectLattice3D(
                a1=np.array([1.0, 0.0, 0.0]),
                a2=np.array([0.0, 1.0, 0.0]),
                a3=np.array([0.0, 0.0, 1.0]),
            ),
            lattice_parameter=ScalarQuantity(5.43, PhysicalUnit("angstrom")),
            atomic_basis=_silicon_basis(),
        )

        restored = UnitCellJsonDeserializer().deserialize(
            UnitCellJsonSerializer().serialize(
                cell,
                structure_id="Si.ConventionalUnitCell",
            ),
            expected_structure_id="Si.ConventionalUnitCell",
        )

        self.assertIsInstance(restored, ConventionalUnitCell)


def _fcc_direct_lattice() -> DirectLattice3D:
    return DirectLattice3D(
        a1=np.array([0.5, 0.5, 0.0]),
        a2=np.array([0.5, 0.0, 0.5]),
        a3=np.array([0.0, 0.5, 0.5]),
    )


def _silicon_basis() -> AtomicBasis:
    return AtomicBasis(
        atoms=(
            Atom(
                symbol="Si",
                position_fractional=VectorQuantity(np.zeros(3), Unitless()),
            ),
            Atom(
                symbol="Si",
                position_fractional=VectorQuantity(
                    np.array([0.25, 0.25, 0.25]), Unitless()
                ),
            ),
        )
    )


if __name__ == "__main__":
    unittest.main()
