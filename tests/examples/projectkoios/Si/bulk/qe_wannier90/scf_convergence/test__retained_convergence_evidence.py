"""Verify the retained bulk-silicon QE convergence evidence boundary."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from examples.projectkoios.Si.bulk.qe_wannier90.scf_convergence.evidence import (
    RetainedArtifactRole,
    RetainedQeScfEvidenceError,
    RetainedQeScfEvidenceLoader,
)
from examples.projectkoios.Si.bulk.qe_wannier90.scf_convergence.replay import (
    RetainedQeScfConvergenceReplayer,
)

_REPOSITORY_ROOT = Path(__file__).resolve().parents[7]
_EXAMPLE_ROOT = (
    _REPOSITORY_ROOT / "examples/projectkoios/Si/bulk/qe_wannier90/scf_convergence"
)
_MANIFEST_PATH = _EXAMPLE_ROOT / "evidence/manifest.json"
_STRUCTURE_PATH = (
    _REPOSITORY_ROOT
    / "examples/projectkoios/Si/single_scf/common/structures/Si.PrimitiveUnitCell.json"
)


class TestRetainedQeScfConvergenceEvidence(unittest.TestCase):
    """Exercise closed loading, identity checks, and calculator-free replay."""

    def test_complete_manifest_and_artifact_identities_load(self) -> None:
        evidence = RetainedQeScfEvidenceLoader(_REPOSITORY_ROOT).load(_MANIFEST_PATH)

        self.assertEqual(evidence.evidence_id, "si-primitive-qe75-actual1-grid")
        self.assertEqual(len(evidence.observations), 36)
        self.assertEqual(
            {item.coordinate.mesh_density for item in evidence.observations},
            {2, 4, 6, 8, 10, 12, 14},
        )
        self.assertEqual(
            {item.coordinate.wavefunction_cutoff_ry for item in evidence.observations},
            {15.0, 20.0, 25.0, 30.0, 35.0, 40.0},
        )
        for observation in evidence.observations:
            self.assertEqual(
                {item.role for item in observation.artifacts},
                set(RetainedArtifactRole),
            )

    def test_replay_reproduces_extension_and_policy_acceptance(self) -> None:
        result = RetainedQeScfConvergenceReplayer(_REPOSITORY_ROOT).replay(
            _MANIFEST_PATH
        )

        self.assertEqual(result.observation_count, 36)
        self.assertEqual(result.warning_count, 144)
        self.assertEqual(len(result.initial_extension.coordinates), 6)
        self.assertEqual(
            {item.mesh_density for item in result.initial_extension.coordinates},
            {12, 14},
        )
        self.assertTrue(result.final_assessment.converged)
        self.assertFalse(result.final_assessment.can_extend)
        self.assertEqual(
            result.final_assessment.kpoint_tail_deltas_mev_per_atom,
            (0.2876923810788412, 0.05986504976362994),
        )
        self.assertEqual(
            result.final_assessment.cutoff_tail_deltas_mev_per_atom,
            (0.5384453053522975, 0.31735279210920453),
        )
        self.assertEqual(result.highest_mesh_density, 14)
        self.assertEqual(result.highest_wavefunction_cutoff_ry, 40.0)

    def test_manifest_rejects_unknown_fields(self) -> None:
        payload = self._manifest_payload()
        payload["unexpected"] = True

        with self.assertRaisesRegex(
            RetainedQeScfEvidenceError, "manifest keys mismatch"
        ):
            self._load_temporary_manifest(payload)

    def test_manifest_rejects_missing_fields(self) -> None:
        payload = self._manifest_payload()
        del payload["evidence_id"]

        with self.assertRaisesRegex(
            RetainedQeScfEvidenceError, "manifest keys mismatch"
        ):
            self._load_temporary_manifest(payload)

    def test_manifest_rejects_duplicate_observations(self) -> None:
        payload = self._manifest_payload()
        observations = payload["observations"]
        assert isinstance(observations, list)
        observations.append(observations[0])

        with self.assertRaisesRegex(
            RetainedQeScfEvidenceError, "run_id values must be unique"
        ):
            self._load_temporary_manifest(payload)

    def test_manifest_rejects_ambiguous_resource_retention(self) -> None:
        payload = self._manifest_payload()
        calculator = payload["calculator"]
        assert isinstance(calculator, dict)
        calculator["retained"] = True

        with self.assertRaisesRegex(
            RetainedQeScfEvidenceError,
            "must not claim unretained bytes are retained",
        ):
            self._load_temporary_manifest(payload)

    def test_manifest_rejects_modified_retained_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository_root = Path(temporary_directory)
            evidence_root = repository_root / "evidence"
            shutil.copytree(_EXAMPLE_ROOT / "evidence", evidence_root)
            shutil.copy2(_STRUCTURE_PATH, repository_root / "structure.json")
            manifest_path = evidence_root / "manifest.json"
            payload = json.loads(manifest_path.read_text())
            payload["structure"]["repository_path"] = "structure.json"
            manifest_path.write_text(json.dumps(payload))
            output_path = evidence_root / "artifacts/actual1-grid-k2-e15/pw.out"
            output_path.write_bytes(output_path.read_bytes() + b"modified\n")

            with self.assertRaisesRegex(
                RetainedQeScfEvidenceError, "artifact byte_size mismatch"
            ):
                RetainedQeScfEvidenceLoader(repository_root).load(manifest_path)

    @staticmethod
    def _manifest_payload() -> dict[str, object]:
        payload = json.loads(_MANIFEST_PATH.read_text())
        assert isinstance(payload, dict)
        return payload

    @staticmethod
    def _load_temporary_manifest(payload: dict[str, object]) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository_root = Path(temporary_directory)
            manifest_path = repository_root / "manifest.json"
            manifest_path.write_text(json.dumps(payload))
            RetainedQeScfEvidenceLoader(repository_root).load(manifest_path)
