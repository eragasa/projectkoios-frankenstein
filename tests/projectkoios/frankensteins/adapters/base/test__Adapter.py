from __future__ import annotations

import unittest

from projectkoios.frankensteins.adapters.base import Adapter, Binding, Integration


class AdapterTest(unittest.TestCase):
    def test_is_the_nominal_base_for_bindings_and_integrations(self) -> None:
        self.assertTrue(issubclass(Binding, Adapter))
        self.assertTrue(issubclass(Integration, Adapter))

    def test_does_not_invent_a_generic_operation(self) -> None:
        self.assertFalse(hasattr(Adapter, "adapt"))
        self.assertFalse(hasattr(Adapter, "execute"))


if __name__ == "__main__":
    unittest.main()
