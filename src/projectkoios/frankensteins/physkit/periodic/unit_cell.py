"""Minimal periodic unit-cell composition shared by calculator adapters."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import numpy as np

from physkit.periodic import DirectLattice3D
from physkit.units import (
    MODEL_SYSTEM_UNIT_CONVERTER,
    MatrixQuantity,
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
    """Compose dimensionless and physical column-basis representations.

    ``A = [a1 a2 a3]`` stores dimensionless direct-lattice vectors as columns. ``H =
    lattice_parameter * A = [h1 h2 h3]`` stores physical cell vectors as columns.
    The explicit pair prevents calculator projections from silently mixing row- and
    column-vector conventions.
    """

    direct_lattice: DirectLattice3D
    lattice_parameter: ScalarQuantity
    atomic_basis: AtomicBasis
    a1: VectorQuantity = field(init=False, repr=False)
    a2: VectorQuantity = field(init=False, repr=False)
    a3: VectorQuantity = field(init=False, repr=False)
    A: MatrixQuantity = field(init=False, repr=False)
    h1: VectorQuantity = field(init=False, repr=False)
    h2: VectorQuantity = field(init=False, repr=False)
    h3: VectorQuantity = field(init=False, repr=False)
    H: MatrixQuantity = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.direct_lattice, DirectLattice3D):
            raise TypeError("direct_lattice must be a DirectLattice3D")
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

        source_a = np.asarray(self.direct_lattice.A, dtype=np.float64)
        canonical_lattice = DirectLattice3D(
            a1=source_a[:, 0],
            a2=source_a[:, 1],
            a3=source_a[:, 2],
        )
        canonical_lattice.A.flags.writeable = False
        a_matrix = MatrixQuantity(magnitude=source_a, unit=Unitless())
        h_matrix = MatrixQuantity(
            magnitude=a_matrix.magnitude * self.lattice_parameter.magnitude,
            unit=self.lattice_parameter.unit,
        )
        object.__setattr__(self, "direct_lattice", canonical_lattice)
        object.__setattr__(self, "A", a_matrix)
        object.__setattr__(self, "H", h_matrix)
        for index, name in enumerate(("a1", "a2", "a3")):
            object.__setattr__(
                self,
                name,
                VectorQuantity(
                    magnitude=a_matrix.magnitude[:, index],
                    unit=Unitless(),
                ),
            )
        for index, name in enumerate(("h1", "h2", "h3")):
            object.__setattr__(
                self,
                name,
                VectorQuantity(
                    magnitude=h_matrix.magnitude[:, index],
                    unit=self.lattice_parameter.unit,
                ),
            )


@dataclass(frozen=True, slots=True)
class ConventionalUnitCell(UnitCell):
    """Identify a unit cell containing a declared conventional representation."""


@dataclass(frozen=True, slots=True)
class PrimitiveUnitCell(UnitCell):
    """Identify a unit cell containing a declared primitive representation."""


@dataclass(frozen=True, slots=True)
class UnitCellJsonSerializer:
    """Serialize reviewed unit-cell values with an explicit representation kind."""

    def serialize(self, unit_cell: UnitCell, *, structure_id: str) -> str:
        """Return deterministic JSON for one conventional or primitive cell."""
        if type(structure_id) is not str or not structure_id:
            raise ValueError("structure_id must be a nonempty string")
        kind_by_type = {
            ConventionalUnitCell: "conventional",
            PrimitiveUnitCell: "primitive",
        }
        kind = kind_by_type.get(type(unit_cell))
        if kind is None:
            raise TypeError(
                "unit_cell must be a ConventionalUnitCell or PrimitiveUnitCell"
            )
        length_unit = unit_cell.lattice_parameter.unit
        if type(length_unit) is not PhysicalUnit:
            raise ValueError("unit-cell lattice parameter must have a physical unit")
        payload = {
            "atoms": [
                {
                    "fractional_position": atom.position_fractional.magnitude.tolist(),
                    "symbol": atom.symbol,
                }
                for atom in unit_cell.atomic_basis.atoms
            ],
            "lattice": {
                "A": {
                    "a1": unit_cell.a1.magnitude.tolist(),
                    "a2": unit_cell.a2.magnitude.tolist(),
                    "a3": unit_cell.a3.magnitude.tolist(),
                    "vector_axis": "columns",
                },
                "lattice_parameter": {
                    "magnitude": unit_cell.lattice_parameter.magnitude,
                    "unit": length_unit.expression,
                },
            },
            "representation": kind,
            "schema_version": 1,
            "structure_id": structure_id,
        }
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"


@dataclass(frozen=True, slots=True)
class UnitCellJsonDeserializer:
    """Deserialize bounded JSON content into an explicit unit-cell subtype."""

    def deserialize(self, content: str, *, expected_structure_id: str) -> UnitCell:
        """Return one validated conventional or primitive unit cell."""
        if type(content) is not str:
            raise TypeError("content must be a string")
        payload = json.loads(content)
        if not isinstance(payload, dict) or payload.get("schema_version") != 1:
            raise ValueError("unsupported unit-cell JSON schema")
        if payload.get("structure_id") != expected_structure_id:
            raise ValueError("structure record identity does not match")
        cell_types: dict[str, type[UnitCell]] = {
            "conventional": ConventionalUnitCell,
            "primitive": PrimitiveUnitCell,
        }
        representation = self._string(payload, "representation")
        cell_type = cell_types.get(representation)
        if cell_type is None:
            raise ValueError("unsupported unit-cell representation")
        lattice = self._mapping(payload, "lattice")
        a_matrix = self._mapping(lattice, "A")
        if self._string(a_matrix, "vector_axis") != "columns":
            raise ValueError("A must declare direct-lattice vectors as columns")
        raw_atoms = payload.get("atoms")
        if not isinstance(raw_atoms, list) or not raw_atoms:
            raise ValueError("atoms must be a nonempty array")
        lattice_parameter = self._mapping(lattice, "lattice_parameter")
        return cell_type(
            direct_lattice=DirectLattice3D(
                a1=np.array(self._triplet(a_matrix, "a1")),
                a2=np.array(self._triplet(a_matrix, "a2")),
                a3=np.array(self._triplet(a_matrix, "a3")),
            ),
            lattice_parameter=ScalarQuantity(
                magnitude=self._number(
                    lattice_parameter.get("magnitude"),
                    "lattice_parameter.magnitude",
                ),
                unit=PhysicalUnit(self._string(lattice_parameter, "unit")),
            ),
            atomic_basis=AtomicBasis(
                atoms=tuple(self._atom(value) for value in raw_atoms)
            ),
        )

    @classmethod
    def _atom(cls, value: object) -> Atom:
        """Decode one atom from JSON data."""
        if not isinstance(value, dict):
            raise ValueError("each atom must be an object")
        return Atom(
            symbol=cls._string(value, "symbol"),
            position_fractional=VectorQuantity(
                magnitude=np.array(cls._triplet(value, "fractional_position")),
                unit=Unitless(),
            ),
        )

    @classmethod
    def _triplet(
        cls,
        mapping: dict[str, object],
        key: str,
    ) -> tuple[float, float, float]:
        """Decode one finite three-component vector."""
        value = mapping.get(key)
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError(f"{key} must contain three numbers")
        numbers = tuple(cls._number(item, key) for item in value)
        return numbers[0], numbers[1], numbers[2]

    @staticmethod
    def _mapping(mapping: dict[str, object], key: str) -> dict[str, object]:
        """Require one nested JSON object."""
        value = mapping.get(key)
        if not isinstance(value, dict):
            raise ValueError(f"{key} must be an object")
        return value

    @staticmethod
    def _string(mapping: dict[str, object], key: str) -> str:
        """Require one nonempty stripped string."""
        value = mapping.get(key)
        if type(value) is not str or not value or value != value.strip():
            raise ValueError(f"{key} must be a nonempty stripped string")
        return value

    @staticmethod
    def _number(value: object, label: str) -> float:
        """Convert one built-in finite JSON number to float."""
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ValueError(f"{label} must be a number")
        number = float(value)
        if not np.isfinite(number):
            raise ValueError(f"{label} must be finite")
        return number
