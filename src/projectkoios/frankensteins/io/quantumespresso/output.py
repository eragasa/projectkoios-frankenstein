"""Bounded extraction of selected observations from ``pw.x`` standard output."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

_MAX_OUTPUT_BYTES = 100_000_000
_FLOAT = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?"
_VERSION = re.compile(r"Program\s+PWSCF\s+v\.([^\s]+)", re.IGNORECASE)
_ATOM_COUNT = re.compile(r"number of atoms/cell\s*=\s*(\d+)", re.IGNORECASE)
_K_POINT_COUNT = re.compile(r"number of k points\s*=\s*(\d+)", re.IGNORECASE)
_CUTOFF = re.compile(rf"kinetic-energy cutoff\s*=\s*({_FLOAT})\s*Ry", re.IGNORECASE)
_TOTAL_ENERGY = re.compile(rf"!\s+total energy\s*=\s*({_FLOAT})\s*Ry", re.IGNORECASE)
_PRESSURE = re.compile(rf"\bP=\s*({_FLOAT})", re.IGNORECASE)
_ITERATION = re.compile(r"^\s*iteration\s+#", re.IGNORECASE)


class QuantumEspressoOutputError(ValueError):
    """Report output text from which no supported ``pw.x`` evidence can be read."""


@dataclass(frozen=True, slots=True)
class PwOutput:
    """Represent selected raw ``pw.x`` observations in their native units."""

    program_version: str | None
    job_completed: bool
    scf_converged: bool
    total_energy_ry: float | None
    wavefunction_cutoff_ry: float | None
    pressure_kbar: float | None
    atom_count: int | None
    k_point_count: int | None
    scf_iteration_count: int

    def __post_init__(self) -> None:
        if self.program_version is not None and not self.program_version:
            raise ValueError("program version must be nonempty when represented")
        for label, value in (
            ("total energy", self.total_energy_ry),
            ("wavefunction cutoff", self.wavefunction_cutoff_ry),
            ("pressure", self.pressure_kbar),
        ):
            if value is not None and not math.isfinite(value):
                raise ValueError(f"{label} must be finite when represented")
        if self.wavefunction_cutoff_ry is not None and self.wavefunction_cutoff_ry <= 0:
            raise ValueError("wavefunction cutoff must be positive")
        if self.atom_count is not None and self.atom_count <= 0:
            raise ValueError("atom count must be positive")
        if self.k_point_count is not None and self.k_point_count <= 0:
            raise ValueError("k-point count must be positive")
        if self.scf_iteration_count < 0:
            raise ValueError("SCF iteration count must be nonnegative")


@dataclass(frozen=True, slots=True)
class PwOutputParser:
    """Extract supported observations from bounded ``pw.x`` output text."""

    def parse(self, text: str) -> PwOutput:
        """Return the last represented scalar value for repeated observations."""
        if type(text) is not str:
            raise TypeError("pw.x output text must be a string")
        if len(text.encode("utf-8")) > _MAX_OUTPUT_BYTES:
            raise QuantumEspressoOutputError("pw.x output exceeds the byte limit")

        program_version: str | None = None
        total_energy: float | None = None
        wavefunction_cutoff: float | None = None
        pressure: float | None = None
        atom_count: int | None = None
        k_point_count: int | None = None
        iteration_count = 0
        recognized = False

        for line in text.splitlines():
            if match := _VERSION.search(line):
                program_version = match.group(1)
                recognized = True
            if match := _ATOM_COUNT.search(line):
                atom_count = int(match.group(1))
                recognized = True
            if match := _K_POINT_COUNT.search(line):
                k_point_count = int(match.group(1))
                recognized = True
            if match := _CUTOFF.search(line):
                wavefunction_cutoff = _native_float(match.group(1))
                recognized = True
            if match := _TOTAL_ENERGY.search(line):
                total_energy = _native_float(match.group(1))
                recognized = True
            if match := _PRESSURE.search(line):
                pressure = _native_float(match.group(1))
                recognized = True
            if _ITERATION.search(line):
                iteration_count += 1
                recognized = True

        if not recognized:
            raise QuantumEspressoOutputError(
                "text contains no supported pw.x output observations"
            )
        lowered = text.casefold()
        return PwOutput(
            program_version=program_version,
            job_completed="job done." in lowered,
            scf_converged="convergence has been achieved" in lowered,
            total_energy_ry=total_energy,
            wavefunction_cutoff_ry=wavefunction_cutoff,
            pressure_kbar=pressure,
            atom_count=atom_count,
            k_point_count=k_point_count,
            scf_iteration_count=iteration_count,
        )


def _native_float(value: str) -> float:
    return float(value.replace("D", "E").replace("d", "e"))
