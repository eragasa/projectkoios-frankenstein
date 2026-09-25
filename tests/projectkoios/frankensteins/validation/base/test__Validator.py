from __future__ import annotations

import unittest
from dataclasses import dataclass

from projectkoios.frankensteins.validation.base import (
    ValidationRequest,
    ValidationResult,
    Validator,
)


@dataclass(frozen=True, slots=True)
class _Request(ValidationRequest):
    value: int


@dataclass(frozen=True, slots=True)
class _Result(ValidationResult):
    accepted: bool

    @property
    def is_valid(self) -> bool:
        return self.accepted


class _Validator(Validator[_Request, _Result]):
    def validate(self, request: _Request, /) -> _Result:
        return _Result(accepted=request.value >= 0)


class ValidatorTest(unittest.TestCase):
    def test_is_a_nominal_request_to_result_action(self) -> None:
        validator = _Validator()
        request = _Request(value=1)

        result = validator.validate(request)

        self.assertIsInstance(request, ValidationRequest)
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid)

    def test_invalid_subject_returns_an_invalid_result(self) -> None:
        result = _Validator().validate(_Request(value=-1))

        self.assertFalse(result.is_valid)


if __name__ == "__main__":
    unittest.main()
