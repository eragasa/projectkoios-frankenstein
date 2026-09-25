"""Minimal periodic unit-cell composition shared by calculator adapters."""

from __future__ import annotations

import re
from dataclasses import dataclass

from physkit.periodic import DirectLattice3D
from physkit.units import (
    MODEL_SYSTEM_UNIT_CONVERTER,
    PhysicalUnit,
    ScalarQuantity,
    Unitless,
    VectorQuantity,
)

_ELEMENT_SYMBOL = re.compile(r"[A-Z][a-z]?")


@dataclass(frozen=True, slots=True)
class Atom:
    """Represent one chemical symbol at fractional unit-cell coordinates."""

    symbol: str
    position_fractional: VectorQuantity

    def __post_init__(self) -> None:
        if type(self.symbol) is not str or not _ELEMENT_SYMBOL.fullmatch(self.symbol):
            raise ValueError("atom symbol must be an element symbol")
        if type(self.position_fractional) is not VectorQuantity:
            raise TypeError("atom position_fractional must be a VectorQuantity")
        if type(self.position_fractional.unit) is not Unitless:
            raise ValueError("atom position_fractional must be explicitly unitless")
        if self.position_fractional.magnitude.shape != (3,):
            raise ValueError("atom position_fractional must contain three coordinates")


@dataclass(frozen=True, slots=True)
class AtomicBasis:
    """Represent an ordered, nonempty tuple of atoms in one unit cell."""

    atoms: tuple[Atom, ...]

    def __post_init__(self) -> None:
        if type(self.atoms) is not tuple:
            raise TypeError("atomic basis atoms must be a tuple")
        if not self.atoms:
            raise ValueError("atomic basis must contain at least one atom")
        if any(type(atom) is not Atom for atom in self.atoms):
            raise TypeError("atomic basis must contain Atom values")


@dataclass(frozen=True, slots=True)
class UnitCell:
    """Compose one primitive direct lattice with one ordered atomic basis."""

    primitive_lattice: DirectLattice3D
    lattice_parameter: ScalarQuantity
    atomic_basis: AtomicBasis

    def __post_init__(self) -> None:
        if not isinstance(self.primitive_lattice, DirectLattice3D):
            raise TypeError("primitive_lattice must be a DirectLattice3D")
        if type(self.lattice_parameter) is not ScalarQuantity:
            raise TypeError("lattice_parameter must be a ScalarQuantity")
        if type(self.lattice_parameter.unit) is not PhysicalUnit:
            raise ValueError("lattice_parameter must have an explicit physical unit")
        if not MODEL_SYSTEM_UNIT_CONVERTER.compatible(
            self.lattice_parameter.unit, PhysicalUnit("meter")
        ):
            raise ValueError(
                "lattice_parameter must have physical length dimensionality"
            )
        if self.lattice_parameter.magnitude <= 0.0:
            raise ValueError("lattice_parameter must be positive")
        if type(self.atomic_basis) is not AtomicBasis:
            raise TypeError("atomic_basis must be an AtomicBasis")
