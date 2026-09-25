from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from projectkoios.frankensteins.adapters.bindings.numpy.probability import NumpyAdapter
from projectkoios.frankensteins.mathematics.probability import (
    ProbabilityDistributionSampler,
    UniformProbabilityDistributionParameters,
    UniformProbabilityDistributionSampler,
)


class UniformProbabilityDistributionSamplerTest(unittest.TestCase):
    def test_composes_parameters_with_a_supported_adapter(self) -> None:
        parameters = UniformProbabilityDistributionParameters(1.5, 2.5)
        sampler = UniformProbabilityDistributionSampler(
            parameters=parameters,
            adapter=NumpyAdapter(),
        )

        self.assertIsInstance(sampler, ProbabilityDistributionSampler)
        self.assertIs(sampler.parameters, parameters)
        self.assertEqual(sampler.supported_adapters, (NumpyAdapter,))
        self.assertEqual(
            sampler.sample(2, random_seed=7),
            (1.5763082893739573, 2.2799187922401147),
        )
        with self.assertRaises(FrozenInstanceError):
            sampler.parameters = parameters  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
