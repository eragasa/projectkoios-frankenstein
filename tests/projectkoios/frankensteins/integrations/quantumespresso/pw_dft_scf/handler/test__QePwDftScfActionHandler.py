from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from projectkoios.frankensteins.applications.pw_dft_scf.actions import (
    AnalyzePwDftScfOutput,
    RegisterPwDftScfTask,
    SubmitPwDftScfTask,
)
from projectkoios.frankensteins.applications.pw_dft_scf.events import (
    PwDftScfOutputAnalyzed,
    PwDftScfTaskFailed,
    PwDftScfTaskRegistered,
    PwDftScfTaskSubmitted,
)
from projectkoios.frankensteins.applications.pw_dft_scf.handler import (
    PwDftScfActionHandler,
)
from projectkoios.frankensteins.integrations.quantumespresso.execution import (
    QeSimulationExecutor,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_scf import (
    configuration as qe_configuration,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_scf import (
    handler as qe_handler,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_scf import (
    integration as qe_integration,
)
from projectkoios.frankensteins.simulations.execution import (
    CalculatorExecutionError,
    CalculatorExecutionRecord,
    ExecutionStatus,
)
from tests.projectkoios.frankensteins.integrations.quantumespresso.pw_dft_scf import (  # noqa: E501
    support as qe_support,
)


class QePwDftScfActionHandlerTest(unittest.TestCase):
    def test_is_a_concrete_common_handler_for_retained_qe_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            run = _successful_run(root)
            handler = _handler(root, run)

            registered = handler.handle(
                RegisterPwDftScfTask(evaluation_id="silicon-qe")
            )
            analyzed = handler.handle(
                AnalyzePwDftScfOutput(
                    task_id="qe-task",
                    output_artifact_id="run/pw.out",
                )
            )

        self.assertIsInstance(handler, PwDftScfActionHandler)
        self.assertEqual(
            registered,
            (
                PwDftScfTaskRegistered(
                    evaluation_id="silicon-qe",
                    task_id="qe-task",
                ),
            ),
        )
        self.assertIsInstance(analyzed[0], PwDftScfOutputAnalyzed)

    def test_recorded_qe_execution_failure_becomes_a_correlated_event(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            run = root / "run"
            run.mkdir()
            handler = _handler(root, run)
            record = CalculatorExecutionRecord(
                command=(sys.executable, "-in", "pw.in"),
                working_directory=str(run),
                status=ExecutionStatus.failed_preflight,
                returncode=None,
                stdout_filename="pw.out",
                stderr_filename="pw.err",
                required_input_filenames=("pw.in", "Si.upf"),
                error_type="FileNotFoundError",
                error_message="missing pseudopotential",
            )
            error = CalculatorExecutionError(
                record=record,
                record_path=run / "execution.json",
            )

            with patch.object(QeSimulationExecutor, "execute", side_effect=error):
                events = handler.handle(SubmitPwDftScfTask(task_id="qe-task"))

        self.assertIsInstance(events[0], PwDftScfTaskSubmitted)
        self.assertIsInstance(events[1], PwDftScfTaskFailed)
        assert isinstance(events[1], PwDftScfTaskFailed)
        self.assertEqual(events[1].code, "calculator-failed-preflight")


def _handler(root: Path, run: Path) -> qe_handler.QePwDftScfActionHandler:
    integration = qe_integration.QePwDftScfIntegration(
        artifact_root=root,
        projection_configuration=_configuration(),
    )
    task = qe_handler.QePwDftScfTask(
        evaluation_id="silicon-qe",
        task_id="qe-task",
        output_artifact_id="run/pw.out",
        simulation=qe_support.qe_simulation(),
        pseudopotential_repository=qe_support.qe_repository(root),
        executable=Path(sys.executable),
        working_directory=run,
    )
    return qe_handler.QePwDftScfActionHandler(
        integration=integration,
        tasks=(task,),
    )


def _configuration() -> qe_configuration.QeScfProjectionConfiguration:
    return qe_configuration.QeScfProjectionConfiguration(
        species=(
            qe_configuration.QeScfSpeciesConfiguration(
                symbol="Si",
                mass_amu=28.086,
                pseudopotential_filename="Si.upf",
            ),
        )
    )


def _successful_run(root: Path) -> Path:
    run = root / "run"
    run.mkdir()
    (run / "pw.out").write_text(qe_support.QE_PW_OUTPUT, encoding="utf-8")
    (run / "pw.err").write_text("", encoding="utf-8")
    (run / "execution.json").write_text(
        json.dumps(qe_support.QE_SUCCESSFUL_EXECUTION_RECORD),
        encoding="utf-8",
    )
    return run


if __name__ == "__main__":
    unittest.main()
