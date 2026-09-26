from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from projectkoios.frankensteins.integrations.vasp.pw_dft_scf.output_analysis import (
    VaspScfOutputArtifactAnalyzer,
)
from projectkoios.frankensteins.integrations.vasp.pw_dft_scf.projection import (
    VASP_SCF_INTEGRATION_ID,
)
from tests.projectkoios.frankensteins.integrations.vasp.outcar import (
    test__VaspOutcarParser as outcar_test,
)


class VaspScfOutputArtifactAnalyzerTest(unittest.TestCase):
    def test_normalizes_successful_retained_outcar(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            run = root / "run"
            run.mkdir()
            (run / "OUTCAR").write_text(outcar_test.OUTCAR, encoding="utf-8")
            (run / "execution.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "status": "succeeded",
                        "returncode": 0,
                    }
                ),
                encoding="utf-8",
            )

            observation = VaspScfOutputArtifactAnalyzer(root).analyze("run/OUTCAR")

        self.assertEqual(observation.total_energy_ev, -10.84056782)
        self.assertEqual(observation.total_energy_ev_per_atom, -5.42028391)
        self.assertEqual(
            observation.native_artifact.integration_id,
            VASP_SCF_INTEGRATION_ID,
        )
        self.assertTrue(observation.completed)
        self.assertTrue(observation.converged)

    def test_rejects_artifact_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            outside = root.parent / "outside-OUTCAR"
            outside.write_text(outcar_test.OUTCAR, encoding="utf-8")
            try:
                with self.assertRaisesRegex(ValueError, "inside artifact_root"):
                    VaspScfOutputArtifactAnalyzer(root).analyze("../outside-OUTCAR")
            finally:
                outside.unlink()


if __name__ == "__main__":
    unittest.main()
