from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, dataclass

from projectkoios.frankensteins.adapters.base import Adapter, Binding, Integration


@dataclass(frozen=True, slots=True)
class _DependencyBinding(Binding):
    dependency_name: str


class BindingTest(unittest.TestCase):
    def test_is_a_distinct_immutable_adapter_role(self) -> None:
        binding = _DependencyBinding(dependency_name="example-dependency")

        self.assertIsInstance(binding, Binding)
        self.assertIsInstance(binding, Adapter)
        self.assertNotIsInstance(binding, Integration)
        with self.assertRaises(FrozenInstanceError):
            binding.dependency_name = "changed"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
