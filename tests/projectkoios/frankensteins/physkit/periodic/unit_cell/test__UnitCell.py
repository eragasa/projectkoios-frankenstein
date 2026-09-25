from __future__ import annotations

import unittest

import numpy as np
from physkit.periodic import DirectLattice3D
from physkit.units import PhysicalUnit, ScalarQuantity, Unitless, VectorQuantity

from projectkoios.frankensteins.physkit.periodic.unit_cell import (
    Atom,
    AtomicBasis,
    UnitCell,
)


class UnitCellTest(unittest.TestCase):
    def test_composes_dimensionless_lattice_parameter_and_atomic_basis(self) -> None:
        lattice = _fcc_primitive_lattice()
        basis = _silicon_basis()
        lattice_parameter = ScalarQuantity(5.43, PhysicalUnit("angstrom"))

        cell = UnitCell(
            primitive_lattice=lattice,
            lattice_parameter=lattice_parameter,
            atomic_basis=basis,
        )

        self.assertIs(cell.primitive_lattice, lattice)
        self.assertIs(cell.lattice_parameter, lattice_parameter)
        self.assertIs(cell.atomic_basis, basis)

    def test_accepts_lattice_parameter_in_any_physical_length_unit(self) -> None:
        cell = UnitCell(
            primitive_lattice=_fcc_primitive_lattice(),
            lattice_parameter=ScalarQuantity(10.26121286, PhysicalUnit("bohr")),
            atomic_basis=_silicon_basis(),
        )

        self.assertEqual(cell.lattice_parameter.unit.expression, "bohr")

    def test_rejects_non_length_lattice_parameter(self) -> None:
        with self.assertRaisesRegex(ValueError, "length dimensionality"):
            UnitCell(
                primitive_lattice=_fcc_primitive_lattice(),
                lattice_parameter=ScalarQuantity(5.43, PhysicalUnit("electron_volt")),
                atomic_basis=_silicon_basis(),
            )


def _fcc_primitive_lattice() -> DirectLattice3D:
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
