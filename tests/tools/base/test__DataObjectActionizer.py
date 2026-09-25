from __future__ import annotations

import unittest
from dataclasses import dataclass

from tools.base import DataObjectActionizer, DataObjectRequest, DataObjectResult


@dataclass(frozen=True, slots=True)
class _Request(DataObjectRequest):
    value: int


@dataclass(frozen=True, slots=True)
class _Response(DataObjectResult):
    request: _Request
    doubled_value: int


@dataclass(frozen=True, slots=True)
class _Doubler(DataObjectActionizer[_Request, _Response]):
    def actionize(self, request: _Request, /) -> _Response:
        return _Response(request=request, doubled_value=request.value * 2)


class _MissingActionize(DataObjectActionizer[_Request, _Response]):
    pass


class DataObjectActionizerTest(unittest.TestCase):
    def test_requires_the_actionize_implementation_at_runtime(self) -> None:
        with self.assertRaisesRegex(TypeError, "abstract method 'actionize'"):
            _MissingActionize()

    def test_concrete_actionizer_has_nominal_runtime_membership(self) -> None:
        self.assertIsInstance(_Doubler(), DataObjectActionizer)

    def test_actionizes_an_explicit_request_into_a_bound_response(self) -> None:
        request = _Request(value=7)

        response = _Doubler().actionize(request)

        self.assertIs(response.request, request)
        self.assertEqual(response.doubled_value, 14)


if __name__ == "__main__":
    unittest.main()
