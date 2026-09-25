from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
from physkit.periodic import DirectLattice3D
from physkit.units import PhysicalUnit, ScalarQuantity, Unitless, VectorQuantity

from projectkoios.frankensteins.integrations.quantumespresso.input import (
    QePwInputFileAssembler,
)
from projectkoios.frankensteins.integrations.vasp.calculation import (
    VaspCalculationProjector,
)
from projectkoios.frankensteins.io.quantumespresso.input import PwInputGroup
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


class PoscarWriterTest(unittest.TestCase):
    def test_projects_one_silicon_simulation_into_qe_and_vasp(self) -> None:
        unit_cell = _silicon_unit_cell()
        simulation = PwDftSimulation(
            unit_cell=unit_cell,
            settings=PwDftSettings(calculation_type=CalculationType.scf),
        )
        qe_input = QePwInputFileAssembler().assemble(
            simulation,
            groups=(
                PwInputGroup(
                    kind="namelist",
                    tag="&SYSTEM",
                    lines=("ibrav = 0", "nat = 2", "ntyp = 1"),
                ),
            ),
            cell_parameters_unit="angstrom",
            atomic_positions_unit="crystal",
            coordinate_precision=16,
            card_order=(
                "ATOMIC_SPECIES",
                "ATOMIC_POSITIONS",
                "K_POINTS",
                "CELL_PARAMETERS",
            ),
        )
        vasp_calculation = VaspCalculationProjector().project(simulation)
        unit_cell_model = UnitCellModel(unit_cell=simulation.unit_cell)
        model = PoscarModel(
            comment="Silicon primitive cell",
            unit_cell_model=unit_cell_model,
        )

        rendered = PoscarWriter().render(model)

        self.assertIs(qe_input.unit_cell, simulation.unit_cell)
        self.assertIs(
            qe_input.control_block.calculation_type,
            simulation.settings.calculation_type,
        )
        self.assertIs(unit_cell_model.unit_cell, simulation.unit_cell)
        self.assertEqual(
            tuple(
                (assignment.tag, assignment.value)
                for assignment in vasp_calculation.input_file.assignments
            ),
            (("IBRION", "-1"), ("NSW", "0")),
        )
        self.assertEqual(
            rendered,
            "Silicon primitive cell\n"
            "1.0\n"
            "2.7149999999999999 2.7149999999999999 0.0000000000000000\n"
            "2.7149999999999999 0.0000000000000000 2.7149999999999999\n"
            "0.0000000000000000 2.7149999999999999 2.7149999999999999\n"
            "Si\n"
            "2\n"
            "Direct\n"
            "0.0000000000000000 0.0000000000000000 0.0000000000000000\n"
            "0.2500000000000000 0.2500000000000000 0.2500000000000000\n",
        )

    def test_model_delegates_atomic_write_to_writer(self) -> None:
        model = PoscarModel(
            comment="Silicon primitive cell",
            unit_cell_model=UnitCellModel(unit_cell=_silicon_unit_cell()),
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "POSCAR"

            model.write(PoscarWriter(), destination)

            self.assertEqual(
                destination.read_text(encoding="ascii"),
                PoscarWriter().render(model),
            )


def _silicon_unit_cell() -> UnitCell:
    lattice_parameter = 5.43
    half = 0.5
    return UnitCell(
        primitive_lattice=DirectLattice3D(
            a1=np.array([half, half, 0.0]),
            a2=np.array([half, 0.0, half]),
            a3=np.array([0.0, half, half]),
        ),
        lattice_parameter=ScalarQuantity(lattice_parameter, PhysicalUnit("angstrom")),
        atomic_basis=AtomicBasis(
            atoms=(
                _atom((0.0, 0.0, 0.0)),
                _atom((0.25, 0.25, 0.25)),
            )
        ),
    )


def _atom(position: tuple[float, float, float]) -> Atom:
    return Atom(
        symbol="Si",
        position_fractional=VectorQuantity(np.array(position), Unitless()),
    )


if __name__ == "__main__":
    unittest.main()
