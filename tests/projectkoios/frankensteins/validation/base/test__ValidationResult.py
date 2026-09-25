from __future__ import annotations

import inspect
import unittest
from dataclasses import dataclass

from projectkoios.frankensteins.validation.base import ValidationResult


@dataclass(frozen=True, slots=True)
class _Result(ValidationResult):
    accepted: bool

    @property
    def is_valid(self) -> bool:
        return self.accepted


class ValidationResultTest(unittest.TestCase):
    def test_requires_specialized_validity_semantics(self) -> None:
        self.assertTrue(inspect.isabstract(ValidationResult))
        self.assertTrue(_Result(accepted=True).is_valid)
        self.assertFalse(_Result(accepted=False).is_valid)


if __name__ == "__main__":
    unittest.main()
