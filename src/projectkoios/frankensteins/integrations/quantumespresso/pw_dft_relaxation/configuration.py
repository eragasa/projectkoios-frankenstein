"""Explicit QE-native projection policy for structural relaxation."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .declarations import QeRelaxationAtomicSpeciesEntry
from .enumerations import (
    QeRelaxationCellDegreesOfFreedom,
    QeRelaxationCellDynamics,
    QeRelaxationIonDynamics,
)


@dataclass(frozen=True, slots=True)
class QeRelaxationProjectionConfiguration:
    """Declare QE-native choices not implied by generic relaxation intent."""

    species: tuple[QeRelaxationAtomicSpeciesEntry, ...]
    ion_dynamics: QeRelaxationIonDynamics
    cell_dynamics: QeRelaxationCellDynamics | None
    cell_degrees_of_freedom: QeRelaxationCellDegreesOfFreedom | None
    charge_density_cutoff_ratio: float
    electronic_tolerance_ry: float
    prefix: str
    pseudo_dir: str
    outdir: str
    input_filename: str
    coordinate_precision: int

    def __post_init__(self) -> None:
        if not self.species or any(
            type(item) is not QeRelaxationAtomicSpeciesEntry for item in self.species
        ):
            raise TypeError(
                "species must contain QeRelaxationAtomicSpeciesEntry values"
            )
        symbols = tuple(item.symbol for item in self.species)
        filenames = tuple(item.pseudopotential_filename for item in self.species)
        if len(symbols) != len(set(symbols)):
            raise ValueError("species symbols must be unique")
        if len(filenames) != len(set(filenames)):
            raise ValueError("pseudopotential filenames must be unique")
        if type(self.ion_dynamics) is not QeRelaxationIonDynamics:
            raise TypeError("ion_dynamics must be a QeRelaxationIonDynamics")
        if (
            self.cell_dynamics is not None
            and type(self.cell_dynamics) is not QeRelaxationCellDynamics
        ):
            raise TypeError("cell_dynamics must be a QeRelaxationCellDynamics or None")
        if (
            self.cell_degrees_of_freedom is not None
            and type(self.cell_degrees_of_freedom)
            is not QeRelaxationCellDegreesOfFreedom
        ):
            raise TypeError(
                "cell_degrees_of_freedom must be a "
                "QeRelaxationCellDegreesOfFreedom or None"
            )
        for label, value in (
            ("charge_density_cutoff_ratio", self.charge_density_cutoff_ratio),
            ("electronic_tolerance_ry", self.electronic_tolerance_ry),
        ):
            if type(value) is not float or not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{label} must be positive and finite")
        for label, text_value in (
            ("prefix", self.prefix),
            ("pseudo_dir", self.pseudo_dir),
            ("outdir", self.outdir),
        ):
            if (
                type(text_value) is not str
                or not text_value
                or text_value != text_value.strip()
                or "'" in text_value
                or "\n" in text_value
                or "\r" in text_value
            ):
                raise ValueError(f"{label} must be nonempty, stripped, and unquoted")
        if (
            type(self.input_filename) is not str
            or not self.input_filename
            or self.input_filename in {".", ".."}
            or "/" in self.input_filename
            or "\\" in self.input_filename
        ):
            raise ValueError("input_filename must be a basename")
        if type(self.coordinate_precision) is not int or self.coordinate_precision <= 0:
            raise ValueError("coordinate_precision must be a positive integer")
