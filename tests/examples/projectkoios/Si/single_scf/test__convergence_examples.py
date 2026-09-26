from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
_EXAMPLE_ROOT = _REPOSITORY_ROOT / "examples" / "projectkoios" / "Si" / "single_scf"
_RUNNER_CONFIG = _EXAMPLE_ROOT / "workflow/runner/config/runner.toml"
_ENVIRONMENT = {
    **os.environ,
    "PYTHONPATH": os.pathsep.join(
        (str(_REPOSITORY_ROOT / "src"), str(_REPOSITORY_ROOT))
    ),
}
_PLAN_CASES = (
    ("convergence/k_points/vasp/campaign.toml", 3),
    ("convergence/k_points/qe/campaign.toml", 3),
    ("convergence/encut/vasp/campaign.toml", 3),
    ("convergence/encut/qe/campaign.toml", 3),
    ("convergence/cross/vasp/campaign.toml", 9),
    ("convergence/cross/qe/campaign.toml", 9),
)
_MESH_COMPONENTS = {4: 0.0, 6: 0.0005, 8: 0.0007}
_CUTOFF_COMPONENTS = {300.0: 0.0, 350.0: 0.0004, 400.0: 0.0008}
_RIGHT_MESH_COMPONENTS = {4: 0.0, 6: 0.0004, 8: 0.0005}
_RIGHT_CUTOFF_COMPONENTS = {300.0: 0.0, 350.0: 0.0003, 400.0: 0.0005}
_COMPARISON_CASES = (
    (
        "convergence/k_points/comparator/comparison.toml",
        ((4, 400.0), (6, 400.0), (8, 400.0)),
    ),
    (
        "convergence/encut/comparator/comparison.toml",
        ((8, 300.0), (8, 350.0), (8, 400.0)),
    ),
    (
        "convergence/cross/comparator/comparison.toml",
        tuple((mesh, cutoff) for mesh in (4, 6, 8) for cutoff in (300.0, 350.0, 400.0)),
    ),
)


class ConvergenceExamplesTest(unittest.TestCase):
    def test_backend_campaigns_render_validated_coordinate_plans(self) -> None:
        for relative_campaign, expected_count in _PLAN_CASES:
            with self.subTest(campaign=relative_campaign):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(_EXAMPLE_ROOT / "workflow" / "runner" / "plan.py"),
                        str(_EXAMPLE_ROOT / relative_campaign),
                        "--runner-config",
                        str(_RUNNER_CONFIG),
                    ],
                    cwd=_REPOSITORY_ROOT,
                    env=_ENVIRONMENT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                payload = json.loads(completed.stdout)
                self.assertEqual(len(payload["coordinates"]), expected_count)

    def test_three_comparator_examples_reassess_independent_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            for index, (relative_comparison, coordinates) in enumerate(
                _COMPARISON_CASES
            ):
                with self.subTest(comparison=relative_comparison):
                    left_path = temporary_root / f"left-{index}.json"
                    right_path = temporary_root / f"right-{index}.json"
                    _write_evidence(
                        path=left_path,
                        evidence_id=f"qe-evidence-{index}",
                        coordinates=coordinates,
                        energy_zero=-5.0,
                        mesh_components=_MESH_COMPONENTS,
                        cutoff_components=_CUTOFF_COMPONENTS,
                    )
                    _write_evidence(
                        path=right_path,
                        evidence_id=f"vasp-evidence-{index}",
                        coordinates=coordinates,
                        energy_zero=-150.0,
                        mesh_components=_RIGHT_MESH_COMPONENTS,
                        cutoff_components=_RIGHT_CUTOFF_COMPONENTS,
                    )
                    completed = subprocess.run(
                        [
                            sys.executable,
                            str(
                                _EXAMPLE_ROOT
                                / "workflow"
                                / "runner"
                                / "compare_convergence.py"
                            ),
                            str(_EXAMPLE_ROOT / relative_comparison),
                            "--runner-config",
                            str(_RUNNER_CONFIG),
                            "--left-evidence",
                            str(left_path),
                            "--right-evidence",
                            str(right_path),
                        ],
                        cwd=_REPOSITORY_ROOT,
                        env=_ENVIRONMENT,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    analysis = json.loads(completed.stdout)
                    self.assertTrue(analysis["left_assessment"]["converged"])
                    self.assertTrue(analysis["right_assessment"]["converged"])
                    self.assertTrue(analysis["convergence_outcomes_match"])


def _write_evidence(
    *,
    path: Path,
    evidence_id: str,
    coordinates: tuple[tuple[int, float], ...],
    energy_zero: float,
    mesh_components: dict[int, float],
    cutoff_components: dict[float, float],
) -> None:
    observations = [
        {
            "mesh_density": mesh,
            "wavefunction_cutoff_ev": cutoff,
            "total_energy_ev_per_atom": (
                energy_zero - mesh_components[mesh] - cutoff_components[cutoff]
            ),
        }
        for mesh, cutoff in coordinates
    ]
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "evidence_id": evidence_id,
                "observations": observations,
            }
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
