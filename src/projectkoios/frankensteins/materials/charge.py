"""Declare unit-cell charge targets and compile stoichiometric constraints."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import reduce
from math import gcd

from physkit.periodic import DirectLattice3D, ReciprocalLattice3D

_ELEMENT_SYMBOL = re.compile(r"^[A-Z][a-z]?$", re.ASCII)


class ChargeConstraintError(ValueError):
    """A charge declaration, constraint, or resolution is invalid."""


def _require_finite(value: float, name: str) -> None:
    if not math.isfinite(value):
        raise ChargeConstraintError(f"{name} must be finite")


@dataclass(frozen=True, slots=True)
class SpeciesMultiplicity:
    """Multiplicity of one chemical species in a unit cell."""

    species: str
    count: int

    def __post_init__(self) -> None:
        if not _ELEMENT_SYMBOL.fullmatch(self.species):
            raise ChargeConstraintError(
                f"invalid chemical species symbol: {self.species!r}"
            )
        if not isinstance(self.count, int) or isinstance(self.count, bool):
            raise ChargeConstraintError("species multiplicity count must be an integer")
        if self.count <= 0:
            raise ChargeConstraintError("species multiplicity count must be positive")


@dataclass(slots=True)
class UnitCellDeclaration:
    """Mutable unit-cell declaration used by the concise authoring DSL."""

    direct_lattice: DirectLattice3D
    species_multiplicities: tuple[SpeciesMultiplicity, ...]
    _charge: float | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.direct_lattice, DirectLattice3D):
            raise ChargeConstraintError(
                "unit-cell direct_lattice must be a PhysKit DirectLattice3D"
            )
        if not self.species_multiplicities:
            raise ChargeConstraintError(
                "unit cell must declare at least one species multiplicity"
            )
        species = tuple(item.species for item in self.species_multiplicities)
        if len(set(species)) != len(species):
            raise ChargeConstraintError(
                "unit-cell species multiplicities must have unique species"
            )

    @property
    def reciprocal_lattice(self) -> ReciprocalLattice3D:
        """Return the PhysKit reciprocal lattice derived from the direct one."""

        return ReciprocalLattice3D.from_direct_lattice(self.direct_lattice)

    @property
    def charge(self) -> float | None:
        """Return the declared target charge, if one has been assigned."""

        return self._charge

    @charge.setter
    def charge(self, value: int | float) -> None:
        if isinstance(value, bool):
            raise ChargeConstraintError("unit-cell charge must be numeric")
        target = float(value)
        _require_finite(target, "unit-cell charge")
        self._charge = target


@dataclass(slots=True)
class StructureDeclaration:
    """Mutable named structure containing one PhysKit-backed unit cell."""

    name: str
    unit_cell: UnitCellDeclaration

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ChargeConstraintError(
                "structure name must be a normalized non-empty string"
            )

    @classmethod
    def from_stoichiometry(
        cls,
        name: str,
        stoichiometry: tuple[tuple[str, int], ...],
        direct_lattice: DirectLattice3D,
        /,
    ) -> StructureDeclaration:
        """Create a named structure from one unit-cell composition."""

        return cls(
            name=name,
            unit_cell=UnitCellDeclaration(
                direct_lattice=direct_lattice,
                species_multiplicities=tuple(
                    SpeciesMultiplicity(species=species, count=count)
                    for species, count in stoichiometry
                ),
            ),
        )


@dataclass(slots=True)
class MaterialSystemDeclaration:
    """Mutable material-system declaration containing named structures."""

    name: str
    structures: dict[str, StructureDeclaration] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ChargeConstraintError(
                "material-system name must be a normalized non-empty string"
            )
        for name, structure in self.structures.items():
            if name != structure.name:
                raise ChargeConstraintError(
                    "structure collection keys must match structure names"
                )

    def add_structure(self, structure: StructureDeclaration, /) -> None:
        """Associate one uniquely named structure with the material system."""

        if structure.name in self.structures:
            raise ChargeConstraintError(
                f"duplicate material-system structure: {structure.name}"
            )
        self.structures[structure.name] = structure

    def structure(self, name: str, /) -> StructureDeclaration:
        """Return one named structure or reject an unknown name."""

        try:
            return self.structures[name]
        except KeyError as error:
            raise ChargeConstraintError(
                f"unknown material-system structure: {name}"
            ) from error


@dataclass(frozen=True, slots=True)
class SpeciesChargeParameter:
    """Immutable identity of one chemical species' charge parameter."""

    species: str

    def __post_init__(self) -> None:
        if not _ELEMENT_SYMBOL.fullmatch(self.species):
            raise ChargeConstraintError(
                f"invalid chemical species symbol: {self.species!r}"
            )

    @property
    def name(self) -> str:
        """Return the stable dotted parameter name used at API boundaries."""

        return f"{self.species}.charge"


@dataclass(frozen=True, slots=True)
class StoichiometricChargeTerm:
    """One coefficient and species-charge parameter in a linear constraint."""

    coefficient: int
    parameter: SpeciesChargeParameter

    def __post_init__(self) -> None:
        if isinstance(self.coefficient, bool) or self.coefficient <= 0:
            raise ChargeConstraintError(
                "stoichiometric charge coefficient must be positive"
            )


@dataclass(frozen=True, slots=True)
class StoichiometricChargeConstraint:
    """Immutable normalized unit-cell total-charge equality constraint."""

    scope: str
    terms: tuple[StoichiometricChargeTerm, ...]
    target_charge: float

    def __post_init__(self) -> None:
        if not self.scope or self.scope.strip() != self.scope:
            raise ChargeConstraintError(
                "constraint scope must be a normalized non-empty string"
            )
        if not self.terms:
            raise ChargeConstraintError("charge constraint must contain terms")
        names = tuple(term.parameter.name for term in self.terms)
        if len(set(names)) != len(names):
            raise ChargeConstraintError(
                "charge constraint parameter identities must be unique"
            )
        _require_finite(self.target_charge, "target_charge")


@dataclass(frozen=True, slots=True)
class ResolvedSpeciesCharge:
    """One immutable resolved value for a species-charge parameter."""

    parameter: SpeciesChargeParameter
    value: float

    def __post_init__(self) -> None:
        _require_finite(self.value, f"resolved value for {self.parameter.name}")


class UnitCellChargeConstraintCompiler:
    """Compile a declarative unit-cell charge target into a linear constraint."""

    def compile(
        self,
        material_system: MaterialSystemDeclaration,
        structure_name: str,
        /,
    ) -> StoichiometricChargeConstraint:
        """Compile one named structure's normalized unit-cell constraint."""

        structure = material_system.structure(structure_name)
        unit_cell = structure.unit_cell
        if unit_cell.charge is None:
            raise ChargeConstraintError(
                "unit-cell charge must be assigned before constraint compilation"
            )

        divisor = reduce(
            gcd,
            (item.count for item in unit_cell.species_multiplicities),
        )
        terms = tuple(
            StoichiometricChargeTerm(
                coefficient=item.count // divisor,
                parameter=SpeciesChargeParameter(item.species),
            )
            for item in unit_cell.species_multiplicities
        )
        return StoichiometricChargeConstraint(
            scope=(f"{material_system.name}.structures[{structure.name!r}].unit_cell"),
            terms=terms,
            target_charge=unit_cell.charge / divisor,
        )


@dataclass(frozen=True, slots=True)
class StoichiometricChargeConstraintResolver:
    """Validate a complete assignment or solve a single unknown charge."""

    absolute_tolerance: float = 1.0e-12

    def __post_init__(self) -> None:
        _require_finite(self.absolute_tolerance, "absolute_tolerance")
        if self.absolute_tolerance < 0.0:
            raise ChargeConstraintError("absolute_tolerance must be nonnegative")

    def resolve(
        self,
        constraint: StoichiometricChargeConstraint,
        known_values: Mapping[str, float],
        /,
    ) -> tuple[ResolvedSpeciesCharge, ...]:
        """Return a complete charge assignment or reject an unsolved system."""

        parameter_names = tuple(term.parameter.name for term in constraint.terms)
        unexpected_names = set(known_values).difference(parameter_names)
        if unexpected_names:
            unexpected = ", ".join(sorted(unexpected_names))
            raise ChargeConstraintError(f"unexpected charge parameters: {unexpected}")

        checked_values: dict[str, float] = {}
        for name, value in known_values.items():
            if isinstance(value, bool):
                raise ChargeConstraintError(f"known value for {name} must be numeric")
            numeric_value = float(value)
            _require_finite(numeric_value, f"known value for {name}")
            checked_values[name] = numeric_value

        unknown_terms = tuple(
            term
            for term in constraint.terms
            if term.parameter.name not in checked_values
        )
        if len(unknown_terms) > 1:
            raise ChargeConstraintError(
                "charge constraint is underdetermined; exactly one unknown may remain"
            )

        known_total = sum(
            term.coefficient * checked_values[term.parameter.name]
            for term in constraint.terms
            if term.parameter.name in checked_values
        )
        if unknown_terms:
            unknown = unknown_terms[0]
            checked_values[unknown.parameter.name] = (
                constraint.target_charge - known_total
            ) / unknown.coefficient
        elif not math.isclose(
            known_total,
            constraint.target_charge,
            rel_tol=0.0,
            abs_tol=self.absolute_tolerance,
        ):
            raise ChargeConstraintError(
                "complete charge assignment violates the stoichiometric constraint"
            )

        return tuple(
            ResolvedSpeciesCharge(
                parameter=term.parameter,
                value=checked_values[term.parameter.name],
            )
            for term in constraint.terms
        )


__all__ = [
    "ChargeConstraintError",
    "MaterialSystemDeclaration",
    "ResolvedSpeciesCharge",
    "SpeciesChargeParameter",
    "SpeciesMultiplicity",
    "StoichiometricChargeConstraint",
    "StoichiometricChargeConstraintResolver",
    "StoichiometricChargeTerm",
    "StructureDeclaration",
    "UnitCellChargeConstraintCompiler",
    "UnitCellDeclaration",
]
