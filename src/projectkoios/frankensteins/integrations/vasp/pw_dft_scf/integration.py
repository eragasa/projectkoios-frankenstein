"""VASP composition of the calculator-neutral SCF integration contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from projectkoios.frankensteins.applications.pw_dft_scf.base import (
    CalculatorIntegrationId,
    PwDftScfObservation,
    PwDftScfRequest,
)
from projectkoios.frankensteins.applications.pw_dft_scf.integration import (
    PwDftScfInputProjection,
    PwDftScfIntegration,
)
from projectkoios.frankensteins.integrations.vasp.pw_dft_scf.configuration import (
    VaspScfProjectionConfiguration,
)
from projectkoios.frankensteins.integrations.vasp.pw_dft_scf.output_analysis import (
    VaspScfOutputArtifactAnalyzer,
)
from projectkoios.frankensteins.integrations.vasp.pw_dft_scf.projection import (
    VASP_SCF_INTEGRATION_ID,
    VaspScfInputProjector,
)


@dataclass(frozen=True, slots=True)
class VaspScfIntegration(PwDftScfIntegration):
    """Compose maintained VASP projection and retained-output analysis."""

    artifact_root: Path
    projection_configuration: VaspScfProjectionConfiguration

    def __post_init__(self) -> None:
        if not self.artifact_root.is_dir() or self.artifact_root.is_symlink():
            raise ValueError("artifact_root must be an existing nonsymlink directory")
        if type(self.projection_configuration) is not VaspScfProjectionConfiguration:
            raise TypeError(
                "projection_configuration must be a VaspScfProjectionConfiguration"
            )

    @property
    def integration_id(self) -> CalculatorIntegrationId:
        """Return the stable VASP backend identity."""
        return VASP_SCF_INTEGRATION_ID

    def project(self, request: PwDftScfRequest) -> PwDftScfInputProjection:
        """Project common intent through maintained VASP input writers."""
        return VaspScfInputProjector(self.projection_configuration).project(request)

    def analyze(self, output_artifact_id: str) -> PwDftScfObservation:
        """Normalize one retained successful OUTCAR observation."""
        return VaspScfOutputArtifactAnalyzer(self.artifact_root).analyze(
            output_artifact_id
        )
