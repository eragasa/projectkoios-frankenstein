from __future__ import annotations

import unittest

from projectkoios.frankensteins.mathematics.probability import (
    ProbabilityDistributionSamplerAdapter,
    ProbabilityError,
    UniformProbabilityDistribution,
    UniformProbabilityDistributionParameters,
    UniformProbabilityDistributionSamplerValidationRequest,
)
from projectkoios.frankensteins.validation.base import ValidationRequest


class UniformProbabilityDistributionSamplerValidationRequestTest(unittest.TestCase):
    def setUp(self) -> None:
        distribution = UniformProbabilityDistribution(
            UniformProbabilityDistributionParameters(1.5, 2.5),
            adapter=ProbabilityDistributionSamplerAdapter.NUMPY,
        )
        self.sampler = distribution.sampler

    def test_is_a_replayable_validation_request(self) -> None:
        request = UniformProbabilityDistributionSamplerValidationRequest(
            sampler=self.sampler,
            sample_count=10_000,
            random_seed=1729,
        )

        self.assertIsInstance(request, ValidationRequest)
        self.assertIs(request.sampler, self.sampler)
        self.assertEqual(request.bin_count, 20)
        self.assertEqual(request.standard_error_limit, 6.0)

    def test_rejects_invalid_statistical_controls(self) -> None:
        for field, value in (
            ("sample_count", 0),
            ("bin_count", 1),
            ("standard_error_limit", 0.0),
        ):
            arguments = {
                "sampler": self.sampler,
                "sample_count": 10_000,
                "random_seed": 1729,
                "bin_count": 20,
                "standard_error_limit": 6.0,
            }
            arguments[field] = value
            with (
                self.subTest(field=field),
                self.assertRaises(ProbabilityError),
            ):
                UniformProbabilityDistributionSamplerValidationRequest(
                    **arguments  # type: ignore[arg-type]
                )


if __name__ == "__main__":
    unittest.main()
