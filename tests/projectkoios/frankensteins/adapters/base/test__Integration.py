from __future__ import annotations

import unittest
from dataclasses import dataclass

from projectkoios.frankensteins.adapters.base import Adapter, Binding, Integration


@dataclass(frozen=True, slots=True)
class _ClientBinding(Binding):
    dependency_name: str


@dataclass(frozen=True, slots=True)
class _ServiceIntegration(Integration):
    service_name: str
    binding: _ClientBinding


class IntegrationTest(unittest.TestCase):
    def test_contains_a_binding_through_composition(self) -> None:
        binding = _ClientBinding(dependency_name="example-client")
        integration = _ServiceIntegration(
            service_name="example-service",
            binding=binding,
        )

        self.assertIsInstance(integration, Integration)
        self.assertIsInstance(integration, Adapter)
        self.assertNotIsInstance(integration, Binding)
        self.assertIs(integration.binding, binding)
        self.assertFalse(issubclass(Integration, Binding))


if __name__ == "__main__":
    unittest.main()
