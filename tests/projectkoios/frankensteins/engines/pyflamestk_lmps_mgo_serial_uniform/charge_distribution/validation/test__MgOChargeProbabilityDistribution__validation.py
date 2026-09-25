from __future__ import annotations

import unittest

import pytest

from projectkoios.frankensteins.engines.pyflamestk_lmps_mgo_serial_uniform import (
    charge_distribution,
)
from projectkoios.frankensteins.mathematics.probability import (
    UniformProbabilityDistributionSamplerValidationRequest,
    UniformProbabilityDistributionSamplerValidator,
)


@pytest.mark.validation
class MgOChargeProbabilityDistributionValidationTest(unittest.TestCase):
    def test_consumer_distribution_passes_uniform_statistical_validation(
        self,
    ) -> None:
        factory = charge_distribution.MgOChargeProbabilityDistributionFactoryObject()
        distribution = factory.create()

        request = UniformProbabilityDistributionSamplerValidationRequest(
            sampler=distribution.sampler,
            sample_count=500_000,
            random_seed=1729,
        )
        validation = UniformProbabilityDistributionSamplerValidator().validate(request)

        self.assertTrue(validation.is_valid, validation)


if __name__ == "__main__":
    unittest.main()
