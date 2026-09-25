from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from physkit.periodic import DirectLattice3D
from physkit.units import PhysicalUnit, ScalarQuantity, Unitless, VectorQuantity

from projectkoios.frankensteins.integrations.vasp.calculation import (
    VaspCalculationProjector,
)
from projectkoios.frankensteins.io.vasp.incar import (
    IncarAssignment,
    IncarFile,
    IncarWriter,
)
from projectkoios.frankensteins.io.vasp.poscar import (
    PoscarModel,
    PoscarWriter,
    UnitCellModel,
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
        description="Write the project-owned silicon VASP SCF input example."
    )
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    output_directory = arguments.output.resolve()
    output_directory.mkdir(parents=True, exist_ok=True)

    simulation = _silicon_scf_simulation()
    projection = VaspCalculationProjector().project(simulation)
    incar = IncarFile(
        assignments=(
            IncarAssignment(tag="SYSTEM", value="Silicon SCF"),
            IncarAssignment(tag="ISTART", value="0"),
            IncarAssignment(tag="ICHARG", value="2"),
            IncarAssignment(tag="ENCUT", value="400"),
            IncarAssignment(tag="ALGO", value="Normal"),
            IncarAssignment(tag="NELM", value="60"),
            IncarAssignment(tag="EDIFF", value="1e-6"),
            IncarAssignment(tag="ISMEAR", value="0"),
            IncarAssignment(tag="SIGMA", value="0.05"),
            IncarAssignment(tag="ISPIN", value="1"),
            IncarAssignment(tag="LREAL", value=".FALSE."),
            *projection.input_file.assignments,
        )
    )
    (output_directory / "INCAR").write_text(
        IncarWriter().render(incar), encoding="ascii"
    )
    PoscarModel(
        comment="Silicon primitive cell",
        unit_cell_model=UnitCellModel(unit_cell=simulation.unit_cell),
    ).write(PoscarWriter(), output_directory / "POSCAR")
    (output_directory / "KPOINTS").write_text(
        "Automatic mesh\n0\nGamma\n8 8 8\n0 0 0\n",
        encoding="ascii",
    )
    (output_directory / "calculation-projection.json").write_text(
        json.dumps(
            {
                "alignment": projection.alignment.value,
                "calculation_type": simulation.settings.calculation_type.value,
                "qualification": projection.qualification,
                "required_inputs": projection.required_inputs,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="ascii",
    )
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
