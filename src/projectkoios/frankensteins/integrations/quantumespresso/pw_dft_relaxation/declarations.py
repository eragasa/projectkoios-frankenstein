"""Typed QE namelist and data-card declarations for structural relaxation."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Literal

from .enumerations import (
    QeRelaxationCalculation,
    QeRelaxationCellDegreesOfFreedom,
    QeRelaxationCellDynamics,
    QeRelaxationIonDynamics,
)

_ELEMENT = re.compile(r"[A-Z][a-z]?")


@dataclass(frozen=True, slots=True)
class QeRelaxationControlNamelist:
    """Declare relaxation-owned fields of the QE ``&CONTROL`` namelist."""

    calculation: QeRelaxationCalculation
    maximum_ionic_steps: int
    total_energy_tolerance_ry: float
    force_tolerance_ry_per_bohr: float
    print_forces: bool
    calculate_stress: bool
    prefix: str
    pseudo_dir: str
    outdir: str

    def __post_init__(self) -> None:
        if type(self.calculation) is not QeRelaxationCalculation:
            raise TypeError("calculation must be a QeRelaxationCalculation")
        if type(self.maximum_ionic_steps) is not int or self.maximum_ionic_steps <= 0:
            raise ValueError("maximum_ionic_steps must be a positive integer")
        _QeRelaxationDeclarationValidation.positive(
            self.total_energy_tolerance_ry, "total_energy_tolerance_ry"
        )
        _QeRelaxationDeclarationValidation.positive(
            self.force_tolerance_ry_per_bohr, "force_tolerance_ry_per_bohr"
        )
        if (
            type(self.print_forces) is not bool
            or type(self.calculate_stress) is not bool
        ):
            raise TypeError("print_forces and calculate_stress must be booleans")
        for label, value in (
            ("prefix", self.prefix),
            ("pseudo_dir", self.pseudo_dir),
            ("outdir", self.outdir),
        ):
            _QeRelaxationDeclarationValidation.input_string(value, label)


@dataclass(frozen=True, slots=True)
class QeRelaxationSystemNamelist:
    """Declare structure counts and cutoffs in the QE ``&SYSTEM`` namelist."""

    ibrav: int
    atom_count: int
    species_count: int
    wavefunction_cutoff_ry: float
    charge_density_cutoff_ry: float

    def __post_init__(self) -> None:
        if type(self.ibrav) is not int or self.ibrav != 0:
            raise ValueError("the maintained structure projection requires ibrav=0")
        for label, value in (
            ("atom_count", self.atom_count),
            ("species_count", self.species_count),
        ):
            if type(value) is not int or value <= 0:
                raise ValueError(f"{label} must be a positive integer")
        _QeRelaxationDeclarationValidation.positive(
            self.wavefunction_cutoff_ry, "wavefunction_cutoff_ry"
        )
        _QeRelaxationDeclarationValidation.positive(
            self.charge_density_cutoff_ry, "charge_density_cutoff_ry"
        )
        if self.charge_density_cutoff_ry < self.wavefunction_cutoff_ry:
            raise ValueError(
                "charge_density_cutoff_ry must not be below wavefunction cutoff"
            )


@dataclass(frozen=True, slots=True)
class QeRelaxationElectronsNamelist:
    """Declare the electronic threshold in the QE ``&ELECTRONS`` namelist."""

    convergence_tolerance_ry: float

    def __post_init__(self) -> None:
        _QeRelaxationDeclarationValidation.positive(
            self.convergence_tolerance_ry, "convergence_tolerance_ry"
        )


@dataclass(frozen=True, slots=True)
class QeRelaxationIonsNamelist:
    """Declare the native optimizer in the QE ``&IONS`` namelist."""

    ion_dynamics: QeRelaxationIonDynamics

    def __post_init__(self) -> None:
        if type(self.ion_dynamics) is not QeRelaxationIonDynamics:
            raise TypeError("ion_dynamics must be a QeRelaxationIonDynamics")


@dataclass(frozen=True, slots=True)
class QeRelaxationCellNamelist:
    """Declare variable-cell controls in the QE ``&CELL`` namelist."""

    cell_dynamics: QeRelaxationCellDynamics
    target_pressure_kbar: float
    pressure_tolerance_kbar: float
    degrees_of_freedom: QeRelaxationCellDegreesOfFreedom

    def __post_init__(self) -> None:
        if type(self.cell_dynamics) is not QeRelaxationCellDynamics:
            raise TypeError("cell_dynamics must be a QeRelaxationCellDynamics")
        if type(self.target_pressure_kbar) is not float or not math.isfinite(
            self.target_pressure_kbar
        ):
            raise ValueError("target_pressure_kbar must be finite")
        _QeRelaxationDeclarationValidation.positive(
            self.pressure_tolerance_kbar, "pressure_tolerance_kbar"
        )
        if type(self.degrees_of_freedom) is not QeRelaxationCellDegreesOfFreedom:
            raise TypeError(
                "degrees_of_freedom must be a QeRelaxationCellDegreesOfFreedom"
            )


@dataclass(frozen=True, slots=True)
class QeRelaxationAtomicSpeciesEntry:
    """Declare one line of the QE ``ATOMIC_SPECIES`` data card."""

    symbol: str
    mass_amu: float
    pseudopotential_filename: str

    def __post_init__(self) -> None:
        if type(self.symbol) is not str or not _ELEMENT.fullmatch(self.symbol):
            raise ValueError("symbol must be an element symbol")
        _QeRelaxationDeclarationValidation.positive(self.mass_amu, "mass_amu")
        _QeRelaxationDeclarationValidation.basename(
            self.pseudopotential_filename, "pseudopotential_filename"
        )


@dataclass(frozen=True, slots=True)
class QeRelaxationAtomicSpeciesCard:
    """Declare the complete QE ``ATOMIC_SPECIES`` data card."""

    entries: tuple[QeRelaxationAtomicSpeciesEntry, ...]

    def __post_init__(self) -> None:
        if not self.entries or any(
            type(item) is not QeRelaxationAtomicSpeciesEntry for item in self.entries
        ):
            raise TypeError(
                "entries must contain QeRelaxationAtomicSpeciesEntry values"
            )
        symbols = tuple(item.symbol for item in self.entries)
        filenames = tuple(item.pseudopotential_filename for item in self.entries)
        if len(symbols) != len(set(symbols)):
            raise ValueError("species symbols must be unique")
        if len(filenames) != len(set(filenames)):
            raise ValueError("pseudopotential filenames must be unique")


@dataclass(frozen=True, slots=True)
class QeRelaxationCellParametersCard:
    """Declare QE ``CELL_PARAMETERS`` vectors with an explicit unit."""

    unit: Literal["angstrom"]
    vectors: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]

    def __post_init__(self) -> None:
        if self.unit != "angstrom":
            raise ValueError("maintained CELL_PARAMETERS must use angstrom")
        _QeRelaxationDeclarationValidation.matrix(self.vectors, "vectors")


@dataclass(frozen=True, slots=True)
class QeRelaxationAtomicPosition:
    """Declare one QE atomic-position line in fractional coordinates."""

    symbol: str
    fractional_position: tuple[float, float, float]

    def __post_init__(self) -> None:
        if type(self.symbol) is not str or not _ELEMENT.fullmatch(self.symbol):
            raise ValueError("symbol must be an element symbol")
        _QeRelaxationDeclarationValidation.triplet(
            self.fractional_position, "fractional_position"
        )


@dataclass(frozen=True, slots=True)
class QeRelaxationAtomicPositionsCard:
    """Declare QE ``ATOMIC_POSITIONS`` in the crystal basis."""

    unit: Literal["crystal"]
    positions: tuple[QeRelaxationAtomicPosition, ...]

    def __post_init__(self) -> None:
        if self.unit != "crystal":
            raise ValueError("maintained ATOMIC_POSITIONS must use crystal")
        if not self.positions or any(
            type(item) is not QeRelaxationAtomicPosition for item in self.positions
        ):
            raise TypeError("positions must contain QeRelaxationAtomicPosition values")


@dataclass(frozen=True, slots=True)
class QeRelaxationKPointsCard:
    """Declare one automatic QE ``K_POINTS`` mesh and shift."""

    option: Literal["automatic"]
    mesh: tuple[int, int, int]
    shift: tuple[int, int, int]

    def __post_init__(self) -> None:
        if self.option != "automatic":
            raise ValueError("maintained K_POINTS must use automatic")
        if len(self.mesh) != 3 or any(
            type(value) is not int or value <= 0 for value in self.mesh
        ):
            raise ValueError("mesh must contain three positive integers")
        if len(self.shift) != 3 or any(
            type(value) is not int or value not in {0, 1} for value in self.shift
        ):
            raise ValueError("shift must contain three zero-or-one integers")


@dataclass(frozen=True, slots=True)
class QeRelaxationInputDeclaration:
    """Compose the typed QE namelists and cards for one relaxation input."""

    control: QeRelaxationControlNamelist
    system: QeRelaxationSystemNamelist
    electrons: QeRelaxationElectronsNamelist
    ions: QeRelaxationIonsNamelist
    cell: QeRelaxationCellNamelist | None
    atomic_species: QeRelaxationAtomicSpeciesCard
    cell_parameters: QeRelaxationCellParametersCard
    atomic_positions: QeRelaxationAtomicPositionsCard
    k_points: QeRelaxationKPointsCard

    def __post_init__(self) -> None:
        expected_types = (
            (self.control, QeRelaxationControlNamelist, "control"),
            (self.system, QeRelaxationSystemNamelist, "system"),
            (self.electrons, QeRelaxationElectronsNamelist, "electrons"),
            (self.ions, QeRelaxationIonsNamelist, "ions"),
            (self.atomic_species, QeRelaxationAtomicSpeciesCard, "atomic_species"),
            (self.cell_parameters, QeRelaxationCellParametersCard, "cell_parameters"),
            (
                self.atomic_positions,
                QeRelaxationAtomicPositionsCard,
                "atomic_positions",
            ),
            (self.k_points, QeRelaxationKPointsCard, "k_points"),
        )
        for value, expected_type, label in expected_types:
            if type(value) is not expected_type:
                raise TypeError(f"{label} must be a {expected_type.__name__}")
        if self.control.calculation is QeRelaxationCalculation.RELAX:
            if self.cell is not None:
                raise ValueError("relax input must not declare a CELL namelist")
        elif type(self.cell) is not QeRelaxationCellNamelist:
            raise TypeError("vc-relax input must declare a QeRelaxationCellNamelist")
        atom_symbols = {item.symbol for item in self.atomic_positions.positions}
        species_symbols = {item.symbol for item in self.atomic_species.entries}
        if atom_symbols != species_symbols:
            raise ValueError("atomic positions and species must use the same symbols")
        if len(self.atomic_positions.positions) != self.system.atom_count:
            raise ValueError("atomic position count does not match SYSTEM.nat")
        if len(self.atomic_species.entries) != self.system.species_count:
            raise ValueError("species count does not match SYSTEM.ntyp")


class _QeRelaxationDeclarationValidation:
    """Own shared lexical and numerical checks for native declarations."""

    __slots__ = ()

    @staticmethod
    def positive(value: float, label: str) -> None:
        if type(value) is not float or not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"{label} must be positive and finite")

    @staticmethod
    def input_string(value: str, label: str) -> None:
        if (
            type(value) is not str
            or not value
            or value != value.strip()
            or "'" in value
            or "\n" in value
            or "\r" in value
        ):
            raise ValueError(f"{label} must be nonempty, stripped, and unquoted")

    @staticmethod
    def basename(value: str, label: str) -> None:
        if (
            type(value) is not str
            or not value
            or value in {".", ".."}
            or "/" in value
            or "\\" in value
        ):
            raise ValueError(f"{label} must be a basename")

    @staticmethod
    def triplet(value: tuple[float, float, float], label: str) -> None:
        if len(value) != 3 or any(
            type(item) is not float or not math.isfinite(item) for item in value
        ):
            raise ValueError(f"{label} must contain three finite floats")

    @classmethod
    def matrix(
        cls,
        value: tuple[
            tuple[float, float, float],
            tuple[float, float, float],
            tuple[float, float, float],
        ],
        label: str,
    ) -> None:
        if len(value) != 3:
            raise ValueError(f"{label} must contain three vectors")
        for vector in value:
            cls.triplet(vector, label)
