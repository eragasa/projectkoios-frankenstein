from __future__ import annotations

import unittest

from projectkoios.frankensteins.materials.charge import (
    ChargeConstraintError,
    MaterialSystemDeclaration,
    StoichiometricChargeConstraintResolver,
    StructureDeclaration,
    UnitCellChargeConstraintCompiler,
)
from tests.projectkoios.frankensteins.materials.charge.support import (
    cubic_direct_lattice,
)


class StoichiometricChargeConstraintResolverTest(unittest.TestCase):
    def setUp(self) -> None:
        MgO = MaterialSystemDeclaration("MgO")
        MgO.add_structure(
            StructureDeclaration.from_stoichiometry(
                "bulk",
                (("Mg", 1), ("O", 1)),
                cubic_direct_lattice(),
            )
        )
        MgO.structure("bulk").unit_cell.charge = 0
        self.constraint = UnitCellChargeConstraintCompiler().compile(MgO, "bulk")
        self.resolver = StoichiometricChargeConstraintResolver()

    def test_resolves_oxygen_without_collapsing_parameter_identities(self) -> None:
        resolved = self.resolver.resolve(
            self.constraint,
            {"Mg.charge": 2.0},
        )

        self.assertEqual(
            tuple((item.parameter.name, item.value) for item in resolved),
            (("Mg.charge", 2.0), ("O.charge", -2.0)),
        )

    def test_can_resolve_magnesium_from_a_known_oxygen_charge(self) -> None:
        resolved = self.resolver.resolve(
            self.constraint,
            {"O.charge": -1.75},
        )

        self.assertEqual(
            tuple((item.parameter.name, item.value) for item in resolved),
            (("Mg.charge", 1.75), ("O.charge", -1.75)),
        )

    def test_validates_a_complete_assignment(self) -> None:
        resolved = self.resolver.resolve(
            self.constraint,
            {"Mg.charge": 2.0, "O.charge": -2.0},
        )

        self.assertEqual(len(resolved), 2)

        with self.assertRaisesRegex(ChargeConstraintError, "violates"):
            self.resolver.resolve(
                self.constraint,
                {"Mg.charge": 2.0, "O.charge": -1.0},
            )

    def test_rejects_an_underdetermined_or_unexpected_assignment(self) -> None:
        with self.assertRaisesRegex(ChargeConstraintError, "underdetermined"):
            self.resolver.resolve(self.constraint, {})

        with self.assertRaisesRegex(ChargeConstraintError, "unexpected"):
            self.resolver.resolve(
                self.constraint,
                {"Mg.charge": 2.0, "Si.charge": 0.0},
            )


if __name__ == "__main__":
    unittest.main()
