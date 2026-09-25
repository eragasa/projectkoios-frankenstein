from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path

from projectkoios.frankensteins.integrations import BaseExecutor


class _RecordingExecutor(BaseExecutor[str, tuple[str, Path]]):
    @property
    def application_name(self) -> str:
        return "recording-application"

    def execute(self, request: str, *, workspace: Path) -> tuple[str, Path]:
        return request, workspace


class _MissingExecute(BaseExecutor[str, str]):
    @property
    def application_name(self) -> str:
        return "missing-execute"


class BaseExecutorTest(unittest.TestCase):
    def test_is_abstract_until_an_integration_supplies_execute(self) -> None:
        self.assertTrue(inspect.isabstract(BaseExecutor))
        self.assertTrue(inspect.isabstract(_MissingExecute))

        with self.assertRaises(TypeError):
            _MissingExecute()  # type: ignore[abstract]

    def test_defines_a_typed_application_and_workspace_boundary(self) -> None:
        executor = _RecordingExecutor()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)

            result = executor.execute("request", workspace=workspace)

        self.assertEqual(executor.application_name, "recording-application")
        self.assertEqual(result, ("request", workspace))

    def test_does_not_supply_process_execution_implicitly(self) -> None:
        self.assertNotIn("subprocess", BaseExecutor.__dict__)
        self.assertNotIn("executable", BaseExecutor.__dict__)


if __name__ == "__main__":
    unittest.main()
