from __future__ import annotations

import unittest

import numpy as np
from physkit.units import Unitless, VectorQuantity

from projectkoios.frankensteins.physkit.periodic.unit_cell import Atom, AtomicBasis


class AtomicBasisTest(unittest.TestCase):
    def test_contains_atoms_in_declared_order(self) -> None:
        first = _atom("Si", (0.0, 0.0, 0.0))
        second = _atom("Si", (0.25, 0.25, 0.25))

        basis = AtomicBasis(atoms=(first, second))

        self.assertEqual(basis.atoms, (first, second))

    def test_rejects_empty_basis(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one atom"):
            AtomicBasis(atoms=())


def _atom(symbol: str, position: tuple[float, float, float]) -> Atom:
    return Atom(
        symbol=symbol,
        position_fractional=VectorQuantity(np.array(position), Unitless()),
    )


if __name__ == "__main__":
    unittest.main()
