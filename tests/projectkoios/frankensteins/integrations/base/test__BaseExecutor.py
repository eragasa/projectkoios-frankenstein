from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path

from projectkoios.frankensteins.integrations import base as integration_base


class _RecordingExecutor(integration_base.BaseExecutor[str, tuple[str, Path]]):
    @property
    def application_name(self) -> str:
        return "recording-application"

    def execute(self, request: str, *, workspace: Path) -> tuple[str, Path]:
        return request, workspace


class _MissingExecute(integration_base.BaseExecutor[str, str]):
    @property
    def application_name(self) -> str:
        return "missing-execute"


class BaseExecutorTest(unittest.TestCase):
    def test__BaseExecutor__is_abstract_without_execute(self) -> None:
        self.assertTrue(inspect.isabstract(integration_base.BaseExecutor))
        self.assertTrue(inspect.isabstract(_MissingExecute))

        with self.assertRaises(TypeError):
            _MissingExecute()  # type: ignore[abstract]

    def test__BaseExecutor__defines_typed_workspace_boundary(self) -> None:
        executor = _RecordingExecutor()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)

            result = executor.execute("request", workspace=workspace)

        self.assertEqual(executor.application_name, "recording-application")
        self.assertEqual(result, ("request", workspace))

    def test__BaseExecutor__does_not_supply_process_execution(self) -> None:
        self.assertNotIn("subprocess", integration_base.BaseExecutor.__dict__)
        self.assertNotIn("executable", integration_base.BaseExecutor.__dict__)


if __name__ == "__main__":
    unittest.main()
