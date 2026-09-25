from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, dataclass

from projectkoios.frankensteins.validation.base import ValidationRequest


@dataclass(frozen=True, slots=True)
class _Request(ValidationRequest):
    value: int


class ValidationRequestTest(unittest.TestCase):
    def test_is_an_immutable_nominal_request_base(self) -> None:
        request = _Request(value=1)

        self.assertIsInstance(request, ValidationRequest)
        with self.assertRaises(FrozenInstanceError):
            request.value = 2  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
