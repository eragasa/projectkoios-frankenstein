from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import numpy as np

from examples.projectkoios.Si.single_scf.workflow.runner.compare_single import (
    SingleScfComparisonRunner,
)
from examples.projectkoios.Si.single_scf.workflow.runner.environment import (
    WorkflowRunnerEnvironment,
)
from projectkoios.frankensteins.applications.pw_dft_scf.base import (
    PwDftScfWorkflowSucceeded,
)
from projectkoios.frankensteins.physkit.periodic.unit_cell import (
    ConventionalUnitCell,
    PrimitiveUnitCell,
    UnitCellJsonSerializer,
)

_EXAMPLE_ROOT = Path("examples/projectkoios/Si/single_scf")
_RUNNER_CONFIG = _EXAMPLE_ROOT / "workflow/runner/config/runner.toml"
_EXPECTED_STRUCTURE_ID = "Si.PrimitiveUnitCell"
_EXPECTED_ATOM_COUNT = 2
_EXPECTED_NATIVE_DIFFERENCE_MEV_PER_ATOM = -149951.99718151568
_EXPECTED_ALIGNED_DIFFERENCE_MEV_PER_ATOM = 14.14347415584949


class WorkflowRunnerTest(unittest.TestCase):
    def test_configuration_resolves_the_minimal_structure_repository(self) -> None:
        environment = WorkflowRunnerEnvironment.load(_RUNNER_CONFIG)

        loaded = environment.loader.load(_EXAMPLE_ROOT / "qe/campaign.toml")

        self.assertEqual(loaded.structure_id, _EXPECTED_STRUCTURE_ID)
        unit_cell = loaded.campaign.recipe.base_request.simulation.unit_cell
        self.assertEqual(
            len(unit_cell.atomic_basis.atoms),
            _EXPECTED_ATOM_COUNT,
        )
        np.testing.assert_array_equal(
            unit_cell.A.magnitude,
            np.column_stack(
                (
                    (0.5, 0.5, 0.0),
                    (0.5, 0.0, 0.5),
                    (0.0, 0.5, 0.5),
                )
            ),
        )
        np.testing.assert_array_equal(
            unit_cell.H.magnitude,
            unit_cell.lattice_parameter.magnitude * unit_cell.A.magnitude,
        )
        self.assertIsInstance(unit_cell, PrimitiveUnitCell)
        self.assertEqual(
            (_EXAMPLE_ROOT / "common/structures/Si.PrimitiveUnitCell.json").read_text(
                encoding="utf-8"
            ),
            UnitCellJsonSerializer().serialize(
                unit_cell,
                structure_id="Si.PrimitiveUnitCell",
            ),
        )

    def test_repository_deserializes_the_named_conventional_cell(self) -> None:
        environment = WorkflowRunnerEnvironment.load(_RUNNER_CONFIG)

        unit_cell = environment.loader.structure_repository.resolve(
            "Si.ConventionalUnitCell"
        )

        self.assertIsInstance(unit_cell, ConventionalUnitCell)
        self.assertEqual(len(unit_cell.atomic_basis.atoms), 8)
        np.testing.assert_array_equal(unit_cell.A.magnitude, np.identity(3))

    def test_single_comparator_uses_only_configured_artifact_declarations(self) -> None:
        environment = WorkflowRunnerEnvironment.load(_RUNNER_CONFIG)

        analysis = SingleScfComparisonRunner(
            environment=environment,
            artifact_root=Path.cwd(),
        ).compare(_EXAMPLE_ROOT / "comparator/comparison.toml")

        self.assertAlmostEqual(
            analysis.native_left_minus_right_mev_per_atom,
            _EXPECTED_NATIVE_DIFFERENCE_MEV_PER_ATOM,
        )
        self.assertAlmostEqual(
            analysis.aligned_left_minus_right_mev_per_atom,
            _EXPECTED_ALIGNED_DIFFERENCE_MEV_PER_ATOM,
        )

    @unittest.skipUnless(importlib.util.find_spec("snakes"), "SNAKES is not installed")
    def test_same_runner_replays_qe_and_vasp_without_calculator_execution(self) -> None:
        from examples.projectkoios.Si.single_scf.workflow.runner.replay import (
            RetainedScfReplayRunner,
        )

        environment = WorkflowRunnerEnvironment.load(_RUNNER_CONFIG)
        runner = RetainedScfReplayRunner(
            environment=environment,
            artifact_root=Path.cwd(),
        )

        for relative_campaign in ("qe/campaign.toml", "vasp/campaign.toml"):
            with self.subTest(campaign=relative_campaign):
                outcome = runner.replay(_EXAMPLE_ROOT / relative_campaign)
                self.assertIsInstance(outcome, PwDftScfWorkflowSucceeded)


if __name__ == "__main__":
    unittest.main()
