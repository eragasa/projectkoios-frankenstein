from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from projectkoios.frankensteins.materials.charge import (
    ChargeConstraintError,
    MaterialSystemDeclaration,
    StoichiometricChargeConstraint,
    StructureDeclaration,
    UnitCellChargeConstraintCompiler,
)
from tests.projectkoios.frankensteins.materials.charge.support import (
    cubic_direct_lattice,
)


class UnitCellChargeConstraintCompilerTest(unittest.TestCase):
    def test_compiles_one_named_structure_in_a_material_system(self) -> None:
        MgO = MaterialSystemDeclaration("MgO")
        MgO.add_structure(
            StructureDeclaration.from_stoichiometry(
                "bulk",
                (("Mg", 1), ("O", 1)),
                cubic_direct_lattice(),
            )
        )
        MgO.structure("bulk").unit_cell.charge = 0

        constraint = UnitCellChargeConstraintCompiler().compile(MgO, "bulk")

        self.assertIsInstance(constraint, StoichiometricChargeConstraint)
        self.assertEqual(
            constraint.scope,
            "MgO.structures['bulk'].unit_cell",
        )
        self.assertEqual(
            tuple((term.coefficient, term.parameter.name) for term in constraint.terms),
            ((1, "Mg.charge"), (1, "O.charge")),
        )
        self.assertEqual(constraint.target_charge, 0.0)

    def test_normalizes_a_conventional_cell_without_losing_the_target(self) -> None:
        MgO = MaterialSystemDeclaration("MgO")
        MgO.add_structure(
            StructureDeclaration.from_stoichiometry(
                "conventional",
                (("Mg", 4), ("O", 4)),
                cubic_direct_lattice(),
            )
        )
        MgO.structure("conventional").unit_cell.charge = 4

        constraint = UnitCellChargeConstraintCompiler().compile(
            MgO,
            "conventional",
        )

        self.assertEqual(
            tuple(term.coefficient for term in constraint.terms),
            (1, 1),
        )
        self.assertEqual(constraint.target_charge, 1.0)

    def test_requires_a_declared_charge_target(self) -> None:
        MgO = MaterialSystemDeclaration("MgO")
        MgO.add_structure(
            StructureDeclaration.from_stoichiometry(
                "bulk",
                (("Mg", 1), ("O", 1)),
                cubic_direct_lattice(),
            )
        )

        with self.assertRaisesRegex(ChargeConstraintError, "must be assigned"):
            UnitCellChargeConstraintCompiler().compile(MgO, "bulk")

    def test_compiled_constraint_is_immutable(self) -> None:
        MgO = MaterialSystemDeclaration("MgO")
        MgO.add_structure(
            StructureDeclaration.from_stoichiometry(
                "bulk",
                (("Mg", 1), ("O", 1)),
                cubic_direct_lattice(),
            )
        )
        MgO.structure("bulk").unit_cell.charge = 0
        constraint = UnitCellChargeConstraintCompiler().compile(MgO, "bulk")

        with self.assertRaises(FrozenInstanceError):
            constraint.target_charge = 2.0  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
