from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
_EXAMPLE_ROOT = _REPOSITORY_ROOT / "examples" / "projectkoios" / "Si" / "scf"


class SiliconScfInputExamplesTest(unittest.TestCase):
    def test_qe_example_reproduces_committed_input(self) -> None:
        self._assert_reproduces("qe/scf", ("pw.in",))

    def test_vasp_example_reproduces_committed_inputs(self) -> None:
        self._assert_reproduces(
            "vasp/scf",
            ("INCAR", "KPOINTS", "POSCAR", "calculation-projection.json"),
        )

    def _assert_reproduces(
        self, relative_example: str, expected_names: tuple[str, ...]
    ) -> None:
        example = _EXAMPLE_ROOT / relative_example
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory)
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(_REPOSITORY_ROOT / "src")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(example / "run.py"),
                    "--output",
                    str(output),
                ],
                cwd=_REPOSITORY_ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                tuple(sorted(path.name for path in output.iterdir())),
                tuple(sorted(expected_names)),
            )
            for name in expected_names:
                self.assertEqual(
                    (output / name).read_bytes(),
                    (example / "input" / name).read_bytes(),
                )


if __name__ == "__main__":
    unittest.main()
