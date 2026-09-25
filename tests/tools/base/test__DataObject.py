from __future__ import annotations

import dataclasses
import unittest
from dataclasses import FrozenInstanceError, dataclass

from tools.base import DataObject


@dataclass(frozen=True, slots=True)
class _ExampleDataObject(DataObject):
    value: str


class DataObjectTest(unittest.TestCase):
    def test_supports_immutable_slotted_domain_subclasses(self) -> None:
        data_object = _ExampleDataObject(value="observed")

        self.assertEqual(data_object.value, "observed")
        self.assertTrue(dataclasses.is_dataclass(data_object))
        self.assertFalse(hasattr(data_object, "__dict__"))
        with self.assertRaises(FrozenInstanceError):
            data_object.value = "changed"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
