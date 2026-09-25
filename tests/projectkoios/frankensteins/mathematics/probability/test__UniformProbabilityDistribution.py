from __future__ import annotations

import math
import unittest
from dataclasses import FrozenInstanceError

from projectkoios.frankensteins.adapters.bindings.numpy.probability import NumpyAdapter
from projectkoios.frankensteins.mathematics.probability import (
    ProbabilityDistribution,
    ProbabilityDistributionSamplerAdapter,
    ProbabilityError,
    UniformProbabilityDistribution,
    UniformProbabilityDistributionParameters,
    UniformProbabilityDistributionSampler,
)


class UniformProbabilityDistributionTest(unittest.TestCase):
    def test_composes_parameters_and_the_selected_sampler(self) -> None:
        parameters = UniformProbabilityDistributionParameters(
            lower_bound=1.5,
            upper_bound=2.5,
        )

        distribution = UniformProbabilityDistribution(
            parameters,
            adapter=ProbabilityDistributionSamplerAdapter.NUMPY,
        )

        self.assertIsInstance(distribution, ProbabilityDistribution)
        self.assertIs(distribution.parameters, parameters)
        self.assertIsInstance(
            distribution.sampler,
            UniformProbabilityDistributionSampler,
        )
        self.assertIs(distribution.sampler.parameters, parameters)
        self.assertIsInstance(distribution.sampler.adapter, NumpyAdapter)
        with self.assertRaises(FrozenInstanceError):
            distribution.parameters = parameters  # type: ignore[misc]

    def test_rejects_nonfinite_or_empty_intervals(self) -> None:
        for lower_bound, upper_bound in (
            (math.nan, 1.0),
            (0.0, math.inf),
            (1.0, 1.0),
            (2.0, 1.0),
        ):
            with (
                self.subTest(lower_bound=lower_bound, upper_bound=upper_bound),
                self.assertRaises(ProbabilityError),
            ):
                UniformProbabilityDistributionParameters(lower_bound, upper_bound)

    def test_rejects_an_unenumerated_adapter(self) -> None:
        parameters = UniformProbabilityDistributionParameters(1.5, 2.5)

        with self.assertRaises(ProbabilityError):
            UniformProbabilityDistribution(
                parameters,
                adapter="numpy",  # type: ignore[arg-type]
            )


if __name__ == "__main__":
    unittest.main()
