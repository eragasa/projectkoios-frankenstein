from __future__ import annotations

import unittest

from projectkoios.frankensteins.core import SourceFileEvidence
from projectkoios.frankensteins.integrations.lammps import (
    inspect_lammps_data_structure,
)


class InspectLammpsDataStructureTest(unittest.TestCase):
    def test_inspects_a_charge_style_orthogonal_structure(self) -> None:
        evidence = SourceFileEvidence("structure_db/unit.structure", "0" * 64, 1)
        text = """# ['Mg', 'O']

2 atoms
2 atom types

0.0 4.0 xlo xhi
0.0 5.0 ylo yhi
0.0 6.0 zlo zhi
0.0 0.0 0.0 xy xz yz

Atoms

1 1 2.0 0.0 0.0 0.0
2 2 -2.0 2.0 2.5 3.0
"""

        observation = inspect_lammps_data_structure(
            name="unit",
            evidence=evidence,
            text=text,
        )

        self.assertEqual(observation.species_order, ("Mg", "O"))
        self.assertEqual(observation.atom_count, 2)
        self.assertEqual(observation.atom_type_count, 2)
        self.assertEqual(observation.atom_style, "charge")
        self.assertEqual(
            observation.bounds,
            ((0.0, 4.0), (0.0, 5.0), (0.0, 6.0)),
        )
        self.assertEqual(observation.tilt_factors, (0.0, 0.0, 0.0))
        self.assertFalse(observation.to_dict()["calculator_execution_authorized"])

    def test_rejects_incomplete_atom_identifiers(self) -> None:
        evidence = SourceFileEvidence("structure_db/unit.structure", "0" * 64, 1)
        text = """# ['Mg']
2 atoms
1 atom types
0.0 4.0 xlo xhi
0.0 4.0 ylo yhi
0.0 4.0 zlo zhi
0.0 0.0 0.0 xy xz yz
Atoms
1 1 0.0 0.0 0.0
3 1 1.0 1.0 1.0
"""

        with self.assertRaisesRegex(ValueError, "identifiers are incomplete"):
            inspect_lammps_data_structure(name="unit", evidence=evidence, text=text)


if __name__ == "__main__":
    unittest.main()
