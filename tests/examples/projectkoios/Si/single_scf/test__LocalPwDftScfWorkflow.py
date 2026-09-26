from __future__ import annotations

import importlib.util
import unittest

from projectkoios.frankensteins.applications.pw_dft_scf.actions import (
    AnalyzePwDftScfOutput,
    RegisterPwDftScfTask,
    SubmitPwDftScfTask,
)
from projectkoios.frankensteins.applications.pw_dft_scf.base import (
    CalculatorIntegrationId,
    PwDftScfNativeArtifact,
    PwDftScfObservation,
    PwDftScfWorkflowFailed,
    PwDftScfWorkflowSucceeded,
)
from projectkoios.frankensteins.applications.pw_dft_scf.configuration import (
    PwDftScfRuntimeConfiguration,
)
from projectkoios.frankensteins.applications.pw_dft_scf.events import (
    PwDftScfOutputAnalyzed,
    PwDftScfTaskCompleted,
    PwDftScfTaskFailed,
    PwDftScfTaskRegistered,
    PwDftScfTaskSubmitted,
)
from projectkoios.frankensteins.applications.pw_dft_scf.handler import (
    MockPwDftScfActionHandler,
    MockPwDftScfTask,
)


@unittest.skipUnless(importlib.util.find_spec("snakes"), "SNAKES is not installed")
class LocalPwDftScfWorkflowTest(unittest.TestCase):
    def test_mock_handler_drives_the_same_net_to_success(self) -> None:
        from examples.projectkoios.Si.single_scf.workflow.dft_pw_scf.workflow import (
            LocalPwDftScfWorkflow,
        )

        workflow = LocalPwDftScfWorkflow(
            "silicon-scf",
            PwDftScfRuntimeConfiguration(),
        )
        handler = MockPwDftScfActionHandler(
            (MockPwDftScfTask("silicon-scf", "task", "mock/output", _observation()),)
        )
        while workflow.outcome() is None:
            actions = workflow.pending_actions()
            self.assertEqual(len(actions), 1)
            for event in handler.handle(actions[0]):
                workflow.accept(event)

        self.assertIsInstance(workflow.outcome(), PwDftScfWorkflowSucceeded)

    def test_reaches_exactly_one_explicit_terminal_outcome(self) -> None:
        from examples.projectkoios.Si.single_scf.workflow.dft_pw_scf.workflow import (
            LocalPwDftScfWorkflow,
        )

        workflow = LocalPwDftScfWorkflow(
            "silicon-scf",
            PwDftScfRuntimeConfiguration(),
        )
        self.assertEqual(
            workflow.pending_actions(),
            (RegisterPwDftScfTask("silicon-scf"),),
        )
        workflow.accept(PwDftScfTaskRegistered("silicon-scf", "task"))
        self.assertEqual(
            workflow.pending_actions(),
            (SubmitPwDftScfTask("task"),),
        )
        workflow.accept(PwDftScfTaskSubmitted("task"))
        workflow.accept(PwDftScfTaskCompleted("task", "run/OUTCAR"))
        self.assertEqual(
            workflow.pending_actions(),
            (AnalyzePwDftScfOutput("task", "run/OUTCAR"),),
        )
        workflow.accept(PwDftScfOutputAnalyzed("task", _observation()))

        self.assertIsInstance(workflow.outcome(), PwDftScfWorkflowSucceeded)
        self.assertEqual(workflow.pending_actions(), ())

    def test_output_analysis_failure_reaches_the_terminal_place(self) -> None:
        from examples.projectkoios.Si.single_scf.workflow.dft_pw_scf.workflow import (
            LocalPwDftScfWorkflow,
        )

        workflow = LocalPwDftScfWorkflow(
            "silicon-scf",
            PwDftScfRuntimeConfiguration(),
        )
        workflow.accept(PwDftScfTaskRegistered("silicon-scf", "task"))
        workflow.accept(PwDftScfTaskSubmitted("task"))
        workflow.accept(PwDftScfTaskCompleted("task", "run/OUTCAR"))
        workflow.accept(
            PwDftScfTaskFailed("task", "output-analysis-failed", "invalid output")
        )

        self.assertIsInstance(workflow.outcome(), PwDftScfWorkflowFailed)
        self.assertEqual(workflow.pending_actions(), ())

    def test_external_failure_reaches_the_same_terminal_place(self) -> None:
        from examples.projectkoios.Si.single_scf.workflow.dft_pw_scf.workflow import (
            LocalPwDftScfWorkflow,
        )

        workflow = LocalPwDftScfWorkflow(
            "silicon-scf",
            PwDftScfRuntimeConfiguration(),
        )
        workflow.accept(PwDftScfTaskRegistered("silicon-scf", "task"))
        workflow.accept(PwDftScfTaskSubmitted("task"))
        workflow.accept(PwDftScfTaskFailed("task", "execution-failed", "failed"))

        self.assertIsInstance(workflow.outcome(), PwDftScfWorkflowFailed)
        self.assertEqual(workflow.pending_actions(), ())


def _observation() -> PwDftScfObservation:
    return PwDftScfObservation(
        total_energy_ev=-10.0,
        atom_count=2,
        electronic_iteration_count=4,
        converged=True,
        completed=True,
        native_artifact=PwDftScfNativeArtifact(
            CalculatorIntegrationId("vasp"),
            "run/OUTCAR",
            "a" * 64,
            100,
        ),
    )


if __name__ == "__main__":
    unittest.main()
