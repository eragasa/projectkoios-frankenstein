from __future__ import annotations

import unittest

from projectkoios.frankensteins.applications.calculator import CalculatorIntegrationId
from projectkoios.frankensteins.applications.pw_dft_relaxation.base import (
    PwDftRelaxationScope,
)
from projectkoios.frankensteins.applications.pw_dft_relaxation.integration import (
    PwDftRelaxationInputWrapper,
    PwDftRelaxationIntegrationRegistry,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_relaxation import (
    configuration as qe_configuration,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_relaxation import (
    declarations as qe_declarations,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_relaxation import (
    enumerations as qe_enumerations,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_relaxation import (
    integration as qe_integration,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_relaxation import (
    projection as qe_projection,
)
from tests.projectkoios.frankensteins.applications.pw_dft_relaxation.support import (
    silicon_relaxation_request,
)

QeRelaxationAtomicSpeciesEntry = qe_declarations.QeRelaxationAtomicSpeciesEntry
QeRelaxationCellNamelist = qe_declarations.QeRelaxationCellNamelist
QeRelaxationCalculation = qe_enumerations.QeRelaxationCalculation
QeRelaxationCellDegreesOfFreedom = qe_enumerations.QeRelaxationCellDegreesOfFreedom
QeRelaxationCellDynamics = qe_enumerations.QeRelaxationCellDynamics
QeRelaxationIonDynamics = qe_enumerations.QeRelaxationIonDynamics
QePwDftRelaxationIntegration = qe_integration.QePwDftRelaxationIntegration
QeRelaxationInputProjector = qe_projection.QeRelaxationInputProjector


class QeRelaxationInputProjectorTest(unittest.TestCase):
    def test_declares_and_renders_fixed_cell_input_by_native_cards(self) -> None:
        projector = QeRelaxationInputProjector(
            configuration=_configuration(variable_cell=False)
        )
        request = silicon_relaxation_request(PwDftRelaxationScope.ATOMIC_POSITIONS)

        declaration = projector.declare(request)
        projection = projector.project(request)

        self.assertIs(declaration.control.calculation, QeRelaxationCalculation.RELAX)
        self.assertIsNone(declaration.cell)
        self.assertEqual(declaration.system.ibrav, 0)
        self.assertEqual(declaration.k_points.mesh, (4, 4, 4))
        text = projection.rendered_inputs[0].text
        self.assertIn("&CONTROL", text)
        self.assertIn("calculation = 'relax'", text)
        self.assertIn("&IONS", text)
        self.assertIn("ion_dynamics = 'bfgs'", text)
        self.assertNotIn("&CELL", text)
        self.assertIn("CELL_PARAMETERS (angstrom)", text)
        self.assertIn("ATOMIC_POSITIONS (crystal)", text)
        self.assertIn("K_POINTS automatic\n 4 4 4 0 0 0", text)
        self.assertEqual(
            projection.required_external_inputs,
            ("Si.test.UPF",),
        )

    def test_declares_and_renders_variable_cell_input_by_native_cards(self) -> None:
        projector = QeRelaxationInputProjector(
            configuration=_configuration(variable_cell=True)
        )
        request = silicon_relaxation_request(
            PwDftRelaxationScope.ATOMIC_POSITIONS_AND_CELL
        )

        declaration = projector.declare(request)
        projection = projector.project(request)

        self.assertIs(
            declaration.control.calculation,
            QeRelaxationCalculation.VC_RELAX,
        )
        self.assertIsInstance(declaration.cell, QeRelaxationCellNamelist)
        text = projection.rendered_inputs[0].text
        self.assertIn("calculation = 'vc-relax'", text)
        self.assertIn("tstress = .true.", text)
        self.assertIn("&CELL", text)
        self.assertIn("cell_dynamics = 'bfgs'", text)
        self.assertIn("cell_dofree = 'all'", text)
        self.assertIn("press = 0.0000000000", text)
        self.assertIn("press_conv_thr = 0.5000000000", text)

    def test_generic_wrapper_selects_installed_qe_integration(self) -> None:
        integration = QePwDftRelaxationIntegration(
            configuration=_configuration(variable_cell=False)
        )
        wrapper = PwDftRelaxationInputWrapper(
            registry=PwDftRelaxationIntegrationRegistry(integrations=(integration,))
        )

        projection = wrapper.project(
            integration_id=CalculatorIntegrationId("quantum-espresso"),
            request=silicon_relaxation_request(PwDftRelaxationScope.ATOMIC_POSITIONS),
        )

        self.assertEqual(projection.integration_id.value, "quantum-espresso")
        with self.assertRaisesRegex(KeyError, "unknown relaxation integration"):
            wrapper.project(
                integration_id=CalculatorIntegrationId("vasp"),
                request=silicon_relaxation_request(
                    PwDftRelaxationScope.ATOMIC_POSITIONS
                ),
            )

    def test_rejects_incompatible_qe_ion_and_cell_algorithms(self) -> None:
        configuration = _configuration(variable_cell=True)
        incompatible = qe_configuration.QeRelaxationProjectionConfiguration(
            species=configuration.species,
            ion_dynamics=QeRelaxationIonDynamics.DAMP,
            cell_dynamics=QeRelaxationCellDynamics.BFGS,
            cell_degrees_of_freedom=configuration.cell_degrees_of_freedom,
            charge_density_cutoff_ratio=configuration.charge_density_cutoff_ratio,
            electronic_tolerance_ry=configuration.electronic_tolerance_ry,
            prefix=configuration.prefix,
            pseudo_dir=configuration.pseudo_dir,
            outdir=configuration.outdir,
            input_filename=configuration.input_filename,
            coordinate_precision=configuration.coordinate_precision,
        )

        with self.assertRaisesRegex(ValueError, "incompatible"):
            QeRelaxationInputProjector(incompatible).declare(
                silicon_relaxation_request(
                    PwDftRelaxationScope.ATOMIC_POSITIONS_AND_CELL
                )
            )

    def test_rejects_documented_but_unimplemented_qe_cell_algorithm(self) -> None:
        configuration = _configuration(variable_cell=True)
        unsupported = qe_configuration.QeRelaxationProjectionConfiguration(
            species=configuration.species,
            ion_dynamics=configuration.ion_dynamics,
            cell_dynamics=QeRelaxationCellDynamics.STEEPEST_DESCENT,
            cell_degrees_of_freedom=configuration.cell_degrees_of_freedom,
            charge_density_cutoff_ratio=configuration.charge_density_cutoff_ratio,
            electronic_tolerance_ry=configuration.electronic_tolerance_ry,
            prefix=configuration.prefix,
            pseudo_dir=configuration.pseudo_dir,
            outdir=configuration.outdir,
            input_filename=configuration.input_filename,
            coordinate_precision=configuration.coordinate_precision,
        )

        with self.assertRaisesRegex(ValueError, "is not supported"):
            QeRelaxationInputProjector(unsupported).declare(
                silicon_relaxation_request(
                    PwDftRelaxationScope.ATOMIC_POSITIONS_AND_CELL
                )
            )


def _configuration(
    *, variable_cell: bool
) -> qe_configuration.QeRelaxationProjectionConfiguration:
    return qe_configuration.QeRelaxationProjectionConfiguration(
        species=(
            QeRelaxationAtomicSpeciesEntry(
                symbol="Si",
                mass_amu=28.086,
                pseudopotential_filename="Si.test.UPF",
            ),
        ),
        ion_dynamics=QeRelaxationIonDynamics.BFGS,
        cell_dynamics=(QeRelaxationCellDynamics.BFGS if variable_cell else None),
        cell_degrees_of_freedom=(
            QeRelaxationCellDegreesOfFreedom.ALL if variable_cell else None
        ),
        charge_density_cutoff_ratio=8.0,
        electronic_tolerance_ry=1.0e-8,
        prefix="system",
        pseudo_dir="./",
        outdir="./tmp/",
        input_filename="pw.in",
        coordinate_precision=8,
    )


if __name__ == "__main__":
    unittest.main()
