from __future__ import annotations

import dataclasses
import unittest

import numpy as np
from physkit.units import PhysicalUnit, Unitless, VectorQuantity

from projectkoios.frankensteins.physkit.periodic.unit_cell import Atom


class AtomTest(unittest.TestCase):
    def test_constructs_element_at_fractional_position(self) -> None:
        position = VectorQuantity(np.array([0.0, 0.25, 0.5]), Unitless())
        atom = Atom(symbol="Si", position_fractional=position)

        self.assertEqual(atom.symbol, "Si")
        self.assertIs(atom.position_fractional, position)
        np.testing.assert_array_equal(
            atom.position_fractional.magnitude, [0.0, 0.25, 0.5]
        )

    def test_is_immutable(self) -> None:
        atom = Atom(
            symbol="Si",
            position_fractional=VectorQuantity(np.zeros(3), Unitless()),
        )

        with self.assertRaises(dataclasses.FrozenInstanceError):
            atom.symbol = "Ge"  # type: ignore[misc]

    def test_rejects_length_unit_for_fractional_position(self) -> None:
        with self.assertRaisesRegex(ValueError, "explicitly unitless"):
            Atom(
                symbol="Si",
                position_fractional=VectorQuantity(
                    np.zeros(3), PhysicalUnit("angstrom")
                ),
            )


if __name__ == "__main__":
    unittest.main()
