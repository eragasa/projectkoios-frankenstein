from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from physkit.periodic import DirectLattice3D
from physkit.units import PhysicalUnit, ScalarQuantity, Unitless, VectorQuantity

from projectkoios.frankensteins.integrations.quantumespresso.input import (
    QePwInputFileAssembler,
)
from projectkoios.frankensteins.io.quantumespresso.input import (
    PwInputGroup,
    PwInputWriter,
)
from projectkoios.frankensteins.physkit.periodic.unit_cell import (
    Atom,
    AtomicBasis,
    UnitCell,
)
from projectkoios.frankensteins.simulations.dft.base import PwDftSimulation
from projectkoios.frankensteins.simulations.dft.settings import (
    CalculationType,
    PwDftSettings,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write the project-owned silicon QE SCF input example."
    )
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    output_directory = arguments.output.resolve()
    output_directory.mkdir(parents=True, exist_ok=True)

    simulation = _silicon_scf_simulation()
    input_file = QePwInputFileAssembler().assemble(
        simulation,
        groups=(
            PwInputGroup(
                kind="namelist",
                tag="&SYSTEM",
                lines=(
                    "ibrav = 0,",
                    "nat = 2,",
                    "ntyp = 1,",
                    "ecutwfc = 30.0,",
                    "ecutrho = 240.0",
                ),
            ),
            PwInputGroup(
                kind="namelist",
                tag="&ELECTRONS",
                lines=("conv_thr = 1.0d-6",),
            ),
            PwInputGroup(
                kind="card",
                tag="ATOMIC_SPECIES",
                lines=("Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF",),
            ),
            PwInputGroup(
                kind="card",
                tag="K_POINTS automatic",
                lines=("8 8 8 0 0 0",),
            ),
        ),
        prefix="system",
        pseudo_dir="./",
        outdir="./tmp/",
        cell_parameters_unit="angstrom",
        atomic_positions_unit="crystal",
        coordinate_precision=8,
        card_order=(
            "ATOMIC_SPECIES",
            "CELL_PARAMETERS",
            "ATOMIC_POSITIONS",
            "K_POINTS",
        ),
    )
    destination = output_directory / "pw.in"
    destination.write_text(PwInputWriter().render(input_file), encoding="ascii")
    print(destination)
    return 0


def _silicon_scf_simulation() -> PwDftSimulation:
    lattice_parameter = 5.43
    half = 0.5
    return PwDftSimulation(
        unit_cell=UnitCell(
            primitive_lattice=DirectLattice3D(
                a1=np.array([half, half, 0.0]),
                a2=np.array([half, 0.0, half]),
                a3=np.array([0.0, half, half]),
            ),
            lattice_parameter=ScalarQuantity(
                lattice_parameter, PhysicalUnit("angstrom")
            ),
            atomic_basis=AtomicBasis(
                atoms=(
                    _silicon_atom((0.0, 0.0, 0.0)),
                    _silicon_atom((0.25, 0.25, 0.25)),
                )
            ),
        ),
        settings=PwDftSettings(calculation_type=CalculationType.scf),
    )


def _silicon_atom(position: tuple[float, float, float]) -> Atom:
    return Atom(
        symbol="Si",
        position_fractional=VectorQuantity(np.array(position), Unitless()),
    )


if __name__ == "__main__":
    raise SystemExit(main())
