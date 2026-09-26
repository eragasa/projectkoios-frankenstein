from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from projectkoios.frankensteins.applications.pw_dft_scf.base import (
    CalculatorIntegrationId,
)
from projectkoios.frankensteins.applications.pw_dft_scf.integration import (
    PwDftScfIntegrationRegistry,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_scf import (
    configuration as qe_configuration,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_scf import (
    integration as qe_integration,
)
from projectkoios.frankensteins.integrations.vasp.pw_dft_scf.configuration import (
    VaspScfProjectionConfiguration,
)
from projectkoios.frankensteins.integrations.vasp.pw_dft_scf.integration import (
    VaspScfIntegration,
)


class QePwDftScfIntegrationTest(unittest.TestCase):
    def test_qe_and_vasp_resolve_by_stable_ids_in_one_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact_root = Path(temporary_directory)
            qe = qe_integration.QePwDftScfIntegration(
                artifact_root=artifact_root,
                projection_configuration=qe_configuration.QeScfProjectionConfiguration(
                    species=(
                        qe_configuration.QeScfSpeciesConfiguration(
                            symbol="Si",
                            mass_amu=28.086,
                            pseudopotential_filename="Si.upf",
                        ),
                    )
                ),
            )
            vasp = VaspScfIntegration(
                artifact_root=artifact_root,
                projection_configuration=VaspScfProjectionConfiguration(),
            )
            registry = PwDftScfIntegrationRegistry(integrations=(qe, vasp))

            resolved_qe = registry.resolve(
                CalculatorIntegrationId(value="quantum-espresso")
            )
            resolved_vasp = registry.resolve(CalculatorIntegrationId(value="vasp"))

        self.assertIs(resolved_qe, qe)
        self.assertIs(resolved_vasp, vasp)


if __name__ == "__main__":
    unittest.main()
