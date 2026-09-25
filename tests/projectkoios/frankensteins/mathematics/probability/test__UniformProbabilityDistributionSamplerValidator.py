from __future__ import annotations

import unittest

from projectkoios.frankensteins.mathematics.probability import (
    ProbabilityDistributionSamplerAdapter,
    UniformProbabilityDistribution,
    UniformProbabilityDistributionParameters,
    UniformProbabilityDistributionSamplerValidation,
    UniformProbabilityDistributionSamplerValidationRequest,
    UniformProbabilityDistributionSamplerValidator,
)
from projectkoios.frankensteins.validation.base import ValidationResult, Validator


class UniformProbabilityDistributionSamplerValidatorTest(unittest.TestCase):
    def test_returns_typed_statistical_validation_evidence(self) -> None:
        distribution = UniformProbabilityDistribution(
            UniformProbabilityDistributionParameters(1.5, 2.5),
            adapter=ProbabilityDistributionSamplerAdapter.NUMPY,
        )
        request = UniformProbabilityDistributionSamplerValidationRequest(
            sampler=distribution.sampler,
            sample_count=10_000,
            random_seed=1729,
            standard_error_limit=100.0,
        )
        validator = UniformProbabilityDistributionSamplerValidator()

        validation = validator.validate(request)

        self.assertIsInstance(validator, Validator)
        self.assertIsInstance(
            validation,
            UniformProbabilityDistributionSamplerValidation,
        )
        self.assertIsInstance(validation, ValidationResult)
        self.assertTrue(validation.is_valid, validation)


if __name__ == "__main__":
    unittest.main()
