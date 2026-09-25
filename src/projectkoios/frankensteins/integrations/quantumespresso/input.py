"""Project calculator-neutral DFT simulations into Quantum ESPRESSO input models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray
from physkit.units import MODEL_SYSTEM_UNIT_CONVERTER, PhysicalUnit

from projectkoios.frankensteins.io.quantumespresso.input import (
    PW_CARD_NAMES,
    ControlBlock,
    PwInputGroup,
    QePwInputFile,
)
from projectkoios.frankensteins.simulations.dft.base import PwDftSimulation


@dataclass(frozen=True, slots=True)
class QePwInputFileAssembler:
    """Assemble typed QE input state from one plane-wave DFT simulation."""

    def assemble(
        self,
        simulation: PwDftSimulation,
        groups: tuple[PwInputGroup, ...],
        *,
        prefix: str | None = None,
        pseudo_dir: str | None = None,
        outdir: str | None = None,
        cell_parameters_unit: Literal["alat", "angstrom", "bohr"],
        atomic_positions_unit: Literal["crystal"],
        coordinate_precision: int,
        card_order: tuple[str, ...],
    ) -> QePwInputFile:
        """Project shared simulation settings and retain its exact unit cell."""
        if type(simulation) is not PwDftSimulation:
            raise TypeError("simulation must be a PwDftSimulation")
        if type(groups) is not tuple:
            raise TypeError("groups must be a tuple")
        generated_card_names = {"ATOMIC_POSITIONS", "CELL_PARAMETERS"}
        if any(
            group.kind == "card"
            and group.tag.split(maxsplit=1)[0].upper() in generated_card_names
            for group in groups
        ):
            raise ValueError("groups must not duplicate generated structure cards")
        combined_groups = (
            *groups,
            *_structure_groups(
                simulation,
                cell_parameters_unit,
                atomic_positions_unit,
                coordinate_precision,
            ),
        )
        namelists = tuple(
            group for group in combined_groups if group.kind == "namelist"
        )
        cards = tuple(group for group in combined_groups if group.kind == "card")
        if type(card_order) is not tuple or len(set(card_order)) != len(card_order):
            raise ValueError("card_order must be a tuple of unique card names")
        card_priority = {name.upper(): index for index, name in enumerate(card_order)}
        default_priority = {
            name: index + len(card_priority) for index, name in enumerate(PW_CARD_NAMES)
        }
        ordered_cards = tuple(
            sorted(
                cards,
                key=lambda group: card_priority.get(
                    group.tag.split(maxsplit=1)[0].upper(),
                    default_priority.get(
                        group.tag.split(maxsplit=1)[0].upper(),
                        len(card_priority) + len(default_priority),
                    ),
                ),
            )
        )
        return QePwInputFile(
            control_block=ControlBlock(
                calculation_type=simulation.settings.calculation_type,
                prefix=prefix,
                pseudo_dir=pseudo_dir,
                outdir=outdir,
            ),
            unit_cell=simulation.unit_cell,
            groups=(*namelists, *ordered_cards),
        )


def _structure_groups(
    simulation: PwDftSimulation,
    cell_parameters_unit: Literal["alat", "angstrom", "bohr"],
    atomic_positions_unit: Literal["crystal"],
    coordinate_precision: int,
) -> tuple[PwInputGroup, ...]:
    if type(coordinate_precision) is not int or coordinate_precision < 1:
        raise ValueError("coordinate_precision must be a positive integer")
    unit_cell = simulation.unit_cell
    factor = 1.0
    if cell_parameters_unit != "alat":
        lattice_parameter = MODEL_SYSTEM_UNIT_CONVERTER.convert_scalar(
            unit_cell.lattice_parameter,
            PhysicalUnit(cell_parameters_unit),
        )
        factor = lattice_parameter.magnitude
    lattice_vectors = (
        unit_cell.primitive_lattice.a1 * factor,
        unit_cell.primitive_lattice.a2 * factor,
        unit_cell.primitive_lattice.a3 * factor,
    )
    return (
        PwInputGroup(
            kind="card",
            tag=f"ATOMIC_POSITIONS ({atomic_positions_unit})",
            lines=tuple(
                atom.symbol
                + " "
                + _format_vector(
                    atom.position_fractional.magnitude,
                    coordinate_precision,
                )
                for atom in unit_cell.atomic_basis.atoms
            ),
        ),
        PwInputGroup(
            kind="card",
            tag=f"CELL_PARAMETERS ({cell_parameters_unit})",
            lines=tuple(
                _format_vector(vector, coordinate_precision)
                for vector in lattice_vectors
            ),
        ),
    )


def _format_vector(vector: NDArray[np.float64], precision: int) -> str:
    first, second, third = vector
    return (
        f"{float(first):.{precision}f} "
        f"{float(second):.{precision}f} "
        f"{float(third):.{precision}f}"
    )
