from __future__ import annotations

import unittest
from pathlib import Path

from examples.projectkoios.Si.single_scf.workflow.runner.environment import (
    WorkflowRunnerEnvironment,
)
from projectkoios.frankensteins.applications.pw_dft_scf.base import (
    CalculatorIntegrationId,
)
from projectkoios.frankensteins.applications.pw_dft_scf.recipe import (
    PwDftScfCutoffConvergenceRecipe,
    PwDftScfGridConvergenceRecipe,
    PwDftScfKpointConvergenceRecipe,
    PwDftScfSingleCalculationRecipe,
)

_EXAMPLE_ROOT = Path("examples/projectkoios/Si/single_scf")
_RUNNER_CONFIG = _EXAMPLE_ROOT / "workflow/runner/config/runner.toml"
_CASES = (
    ("vasp/campaign.toml", "vasp", PwDftScfSingleCalculationRecipe),
    ("qe/campaign.toml", "quantum-espresso", PwDftScfSingleCalculationRecipe),
    (
        "convergence/k_points/vasp/campaign.toml",
        "vasp",
        PwDftScfKpointConvergenceRecipe,
    ),
    (
        "convergence/k_points/qe/campaign.toml",
        "quantum-espresso",
        PwDftScfKpointConvergenceRecipe,
    ),
    (
        "convergence/encut/vasp/campaign.toml",
        "vasp",
        PwDftScfCutoffConvergenceRecipe,
    ),
    (
        "convergence/encut/qe/campaign.toml",
        "quantum-espresso",
        PwDftScfCutoffConvergenceRecipe,
    ),
    (
        "convergence/cross/vasp/campaign.toml",
        "vasp",
        PwDftScfGridConvergenceRecipe,
    ),
    (
        "convergence/cross/qe/campaign.toml",
        "quantum-espresso",
        PwDftScfGridConvergenceRecipe,
    ),
)


class LoadCampaignConfigurationTest(unittest.TestCase):
    def test_loads_the_separate_backend_campaign_examples(self) -> None:
        loader = WorkflowRunnerEnvironment.load(_RUNNER_CONFIG).loader

        for relative_path, integration_id, recipe_type in _CASES:
            with self.subTest(path=relative_path):
                loaded = loader.load(_EXAMPLE_ROOT / relative_path)

                self.assertEqual(
                    loaded.campaign.integration_id,
                    CalculatorIntegrationId(value=integration_id),
                )
                self.assertIsInstance(loaded.campaign.recipe, recipe_type)
                self.assertEqual(
                    loaded.structure_id,
                    "Si.PrimitiveUnitCell",
                )


if __name__ == "__main__":
    unittest.main()
