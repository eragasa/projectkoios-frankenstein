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
from projectkoios.frankensteins.integrations.vasp.pw_dft_scf.configuration import (
    VaspScfProjectionConfiguration,
)
from projectkoios.frankensteins.integrations.vasp.pw_dft_scf.integration import (
    VaspScfIntegration,
)


class VaspScfIntegrationTest(unittest.TestCase):
    def test_is_resolved_by_the_common_source_controlled_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            integration = VaspScfIntegration(
                Path(temporary_directory),
                VaspScfProjectionConfiguration(),
            )
            registry = PwDftScfIntegrationRegistry((integration,))

            resolved = registry.resolve(CalculatorIntegrationId("vasp"))

        self.assertIs(resolved, integration)


if __name__ == "__main__":
    unittest.main()
