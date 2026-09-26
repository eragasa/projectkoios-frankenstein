"""Quantum ESPRESSO implementation of the selectable relaxation integration."""

from __future__ import annotations

from dataclasses import dataclass

from projectkoios.frankensteins.applications.calculator import (
    CalculatorIntegrationId,
)
from projectkoios.frankensteins.applications.pw_dft_relaxation.base import (
    PwDftRelaxationRequest,
)
from projectkoios.frankensteins.applications.pw_dft_relaxation.capabilities import (
    PW_DFT_RELAXATION_BACKEND_DESCRIPTIONS,
    PwDftRelaxationBackendDescription,
)
from projectkoios.frankensteins.applications.pw_dft_relaxation.integration import (
    PwDftRelaxationInputProjection,
    PwDftRelaxationIntegration,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_relaxation import (
    configuration as qe_configuration,
)

from .projection import QeRelaxationInputProjector


@dataclass(frozen=True, slots=True)
class QePwDftRelaxationIntegration(PwDftRelaxationIntegration):
    """Project generic relaxation requests into QE namelists and data cards."""

    configuration: qe_configuration.QeRelaxationProjectionConfiguration

    def __post_init__(self) -> None:
        if (
            type(self.configuration)
            is not qe_configuration.QeRelaxationProjectionConfiguration
        ):
            raise TypeError(
                "configuration must be a QeRelaxationProjectionConfiguration"
            )

    @property
    def description(self) -> PwDftRelaxationBackendDescription:
        """Return the reviewed QE input-family and support description."""
        matches = tuple(
            item
            for item in PW_DFT_RELAXATION_BACKEND_DESCRIPTIONS
            if item.integration_id == CalculatorIntegrationId("quantum-espresso")
        )
        if len(matches) != 1:
            raise RuntimeError("QE relaxation backend description is not unique")
        return matches[0]

    def project(
        self, request: PwDftRelaxationRequest
    ) -> PwDftRelaxationInputProjection:
        """Return deterministic QE input for the selected generic request."""
        return QeRelaxationInputProjector(self.configuration).project(request)
