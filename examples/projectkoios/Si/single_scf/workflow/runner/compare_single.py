"""Common runner for retained silicon single-SCF comparison."""

from __future__ import annotations

import argparse
import json
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

from examples.projectkoios.Si.single_scf.workflow.runner.configuration import (
    LoadedWorkflowRunnerConfiguration,
)
from examples.projectkoios.Si.single_scf.workflow.runner.environment import (
    WorkflowRunnerEnvironment,
)
from projectkoios.frankensteins.applications.pw_dft_scf.base import (
    PwDftScfObservation,
    PwDftScfResult,
)
from projectkoios.frankensteins.applications.pw_dft_scf.comparison import (
    PwDftScfComparator,
    PwDftScfComparisonAnalysis,
    PwDftScfComparisonRequest,
    PwDftScfEnergyAlignment,
    PwDftScfEnergyAlignmentKind,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_scf import (
    output_analysis as qe_output_analysis,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_scf import (
    projection as qe_projection,
)
from projectkoios.frankensteins.integrations.vasp.pw_dft_scf import (
    output_analysis as vasp_output_analysis,
)
from projectkoios.frankensteins.integrations.vasp.pw_dft_scf import (
    projection as vasp_projection,
)


@dataclass(frozen=True, slots=True)
class SingleScfComparisonRunner:
    """Analyze configured retained artifacts through maintained integrations."""

    environment: WorkflowRunnerEnvironment
    artifact_root: Path

    def __post_init__(self) -> None:
        if not self.artifact_root.is_dir() or self.artifact_root.is_symlink():
            raise ValueError("artifact_root must be a nonsymlink directory")

    def compare(self, comparison_path: Path) -> PwDftScfComparisonAnalysis:
        """Return one qualified comparison with no calculator execution."""
        declaration = self._toml(comparison_path)
        left_loaded = self.environment.loader.load(
            self._campaign_path(declaration, "left_campaign", comparison_path)
        )
        right_loaded = self.environment.loader.load(
            self._campaign_path(declaration, "right_campaign", comparison_path)
        )
        alignment = self._mapping(declaration, "alignment")
        request = PwDftScfComparisonRequest(
            comparison_id=self._string(declaration, "comparison_id"),
            input_alignment_id=self._string(
                declaration,
                "input_alignment_id",
            ),
            left=self._alignment(
                loaded=left_loaded,
                declaration=self._mapping(alignment, "left"),
            ),
            right=self._alignment(
                loaded=right_loaded,
                declaration=self._mapping(alignment, "right"),
            ),
        )
        return PwDftScfComparator().compare(request)

    def _alignment(
        self,
        *,
        loaded: LoadedWorkflowRunnerConfiguration,
        declaration: dict[str, object],
    ) -> PwDftScfEnergyAlignment:
        """Analyze one retained campaign and apply declared energy treatment."""
        replay = loaded.replay
        if replay is None:
            raise ValueError("single-SCF comparison campaign lacks replay evidence")
        observation = self._analyze(
            integration_id=loaded.campaign.integration_id.value,
            artifact_id=replay.output_artifact_id,
        )
        result = PwDftScfResult(
            evaluation_id=replay.evaluation_id,
            task_id=replay.task_id,
            observation=observation,
        )
        kind = PwDftScfEnergyAlignmentKind(self._string(declaration, "kind"))
        if kind is PwDftScfEnergyAlignmentKind.NATIVE:
            return PwDftScfEnergyAlignment(result=result)
        return PwDftScfEnergyAlignment(
            result=result,
            kind=kind,
            reference_energy_ev_per_atom=self._float(
                declaration,
                "reference_energy_ev_per_atom",
            ),
            reference_id=self._string(declaration, "reference_id"),
            qualification=self._string(declaration, "qualification"),
        )

    def _analyze(
        self,
        *,
        integration_id: str,
        artifact_id: str,
    ) -> PwDftScfObservation:
        """Dispatch retained analysis through the source-controlled integration set."""
        if integration_id == qe_projection.QE_SCF_INTEGRATION_ID.value:
            return qe_output_analysis.QeScfOutputArtifactAnalyzer(
                artifact_root=self.artifact_root
            ).analyze(artifact_id)
        if integration_id == vasp_projection.VASP_SCF_INTEGRATION_ID.value:
            return vasp_output_analysis.VaspScfOutputArtifactAnalyzer(
                artifact_root=self.artifact_root
            ).analyze(artifact_id)
        raise ValueError(f"unsupported integration: {integration_id}")

    @classmethod
    def _campaign_path(
        cls,
        declaration: dict[str, object],
        key: str,
        comparison_path: Path,
    ) -> Path:
        """Resolve one campaign within the single-SCF example hierarchy."""
        path = (comparison_path.parent / cls._string(declaration, key)).resolve()
        if not path.is_relative_to(comparison_path.parent.parent.resolve()):
            raise ValueError(f"{key} escapes the single-SCF example")
        return path

    @staticmethod
    def _toml(path: Path) -> dict[str, object]:
        """Read one bounded single-SCF comparison declaration."""
        if not path.is_file() or path.is_symlink() or path.stat().st_size > 100_000:
            raise ValueError("comparison declaration must be a bounded regular file")
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != 2:
            raise ValueError("unsupported single-SCF comparison schema")
        return payload

    @staticmethod
    def _mapping(mapping: dict[str, object], key: str) -> dict[str, object]:
        """Require one nested TOML table."""
        value = mapping.get(key)
        if not isinstance(value, dict):
            raise ValueError(f"{key} must be a table")
        return value

    @staticmethod
    def _string(mapping: dict[str, object], key: str) -> str:
        """Require one nonempty stripped string."""
        value = mapping.get(key)
        if type(value) is not str or not value or value != value.strip():
            raise ValueError(f"{key} must be a nonempty stripped string")
        return value

    @staticmethod
    def _float(mapping: dict[str, object], key: str) -> float:
        """Convert one built-in numeric value to float."""
        value = mapping.get(key)
        if type(value) not in {int, float}:
            raise ValueError(f"{key} must be a number")
        return float(value)


@dataclass(frozen=True, slots=True)
class SingleScfComparisonRunnerCommand:
    """Parse command paths and invoke `SingleScfComparisonRunner`."""

    def run(self) -> int:
        """Print one configured retained single-SCF comparison."""
        parser = argparse.ArgumentParser(
            description="Compare configured retained silicon single-SCF results."
        )
        parser.add_argument("comparison", type=Path)
        parser.add_argument("--runner-config", required=True, type=Path)
        parser.add_argument("--artifact-root", required=True, type=Path)
        arguments = parser.parse_args()
        environment = WorkflowRunnerEnvironment.load(arguments.runner_config.resolve())
        analysis = SingleScfComparisonRunner(
            environment=environment,
            artifact_root=arguments.artifact_root.resolve(),
        ).compare(arguments.comparison.resolve())
        print(json.dumps(asdict(analysis), indent=2, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(SingleScfComparisonRunnerCommand().run())
