from __future__ import annotations

import math
import unittest

from physkit.periodic import DirectLattice3D, ReciprocalLattice3D

from projectkoios.frankensteins.materials.charge import (
    ChargeConstraintError,
    MaterialSystemDeclaration,
    StructureDeclaration,
)
from tests.projectkoios.frankensteins.materials.charge.support import (
    cubic_direct_lattice,
)


class MaterialSystemDeclarationTest(unittest.TestCase):
    def test_supports_charge_declarations_on_multiple_named_structures(self) -> None:
        MgO = MaterialSystemDeclaration("MgO")
        MgO.add_structure(
            StructureDeclaration.from_stoichiometry(
                "bulk",
                (("Mg", 1), ("O", 1)),
                cubic_direct_lattice(),
            )
        )
        MgO.add_structure(
            StructureDeclaration.from_stoichiometry(
                "surface_001",
                (("Mg", 2), ("O", 2)),
                cubic_direct_lattice(),
            )
        )

        MgO.structure("bulk").unit_cell.charge = 0
        MgO.structure("surface_001").unit_cell.charge = 0

        bulk = MgO.structure("bulk")
        self.assertIsInstance(bulk.unit_cell.direct_lattice, DirectLattice3D)
        self.assertIsInstance(bulk.unit_cell.reciprocal_lattice, ReciprocalLattice3D)
        self.assertEqual(bulk.unit_cell.charge, 0.0)
        self.assertEqual(
            tuple(
                (item.species, item.count)
                for item in bulk.unit_cell.species_multiplicities
            ),
            (("Mg", 1), ("O", 1)),
        )
        self.assertEqual(tuple(MgO.structures), ("bulk", "surface_001"))

    def test_rejects_invalid_stoichiometry_and_charge(self) -> None:
        with self.assertRaisesRegex(ChargeConstraintError, "positive"):
            StructureDeclaration.from_stoichiometry(
                "bulk",
                (("Mg", 0), ("O", 1)),
                cubic_direct_lattice(),
            )

        structure = StructureDeclaration.from_stoichiometry(
            "bulk",
            (("Mg", 1), ("O", 1)),
            cubic_direct_lattice(),
        )
        with self.assertRaisesRegex(ChargeConstraintError, "finite"):
            structure.unit_cell.charge = math.inf

    def test_rejects_duplicate_and_unknown_structure_names(self) -> None:
        MgO = MaterialSystemDeclaration("MgO")
        bulk = StructureDeclaration.from_stoichiometry(
            "bulk",
            (("Mg", 1), ("O", 1)),
            cubic_direct_lattice(),
        )
        MgO.add_structure(bulk)

        with self.assertRaisesRegex(ChargeConstraintError, "duplicate"):
            MgO.add_structure(bulk)
        with self.assertRaisesRegex(ChargeConstraintError, "unknown"):
            MgO.structure("missing")


if __name__ == "__main__":
    unittest.main()
