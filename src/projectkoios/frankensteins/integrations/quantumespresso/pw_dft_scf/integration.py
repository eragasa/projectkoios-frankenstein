"""Quantum ESPRESSO implementation of the common SCF integration contract."""

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
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_scf import (
    configuration as qe_configuration,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_scf import (
    output_analysis as qe_output_analysis,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_scf import (
    projection as qe_projection,
)


@dataclass(frozen=True, slots=True)
class QePwDftScfIntegration(PwDftScfIntegration):
    """Compose maintained QE projection and retained-output analysis."""

    artifact_root: Path
    projection_configuration: qe_configuration.QeScfProjectionConfiguration

    def __post_init__(self) -> None:
        if not self.artifact_root.is_dir() or self.artifact_root.is_symlink():
            raise ValueError("artifact_root must be an existing nonsymlink directory")
        if (
            type(self.projection_configuration)
            is not qe_configuration.QeScfProjectionConfiguration
        ):
            raise TypeError(
                "projection_configuration must be a QeScfProjectionConfiguration"
            )

    @property
    def integration_id(self) -> CalculatorIntegrationId:
        """Return the stable Quantum ESPRESSO backend identity."""
        return qe_projection.QE_SCF_INTEGRATION_ID

    def project(self, request: PwDftScfRequest) -> PwDftScfInputProjection:
        """Project common intent through the maintained QE input assembler."""
        return qe_projection.QeScfInputProjector(
            configuration=self.projection_configuration
        ).project(request)

    def analyze(self, output_artifact_id: str) -> PwDftScfObservation:
        """Normalize one retained successful ``pw.x`` observation."""
        return qe_output_analysis.QeScfOutputArtifactAnalyzer(
            artifact_root=self.artifact_root
        ).analyze(output_artifact_id)
