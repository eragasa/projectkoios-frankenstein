from __future__ import annotations

import unittest

from projectkoios.frankensteins.engines.pyflamestk_lmps_mgo_serial_uniform import (
    charge_distribution,
)
from projectkoios.frankensteins.mathematics.probability import (
    ProbabilityDistributionSamplerAdapter,
    UniformProbabilityDistribution,
)


class MgOChargeProbabilityDistributionFactoryObjectTest(unittest.TestCase):
    def test_creates_the_historical_magnesium_charge_distribution(self) -> None:
        factory = charge_distribution.MgOChargeProbabilityDistributionFactoryObject()

        distribution = factory.create()

        self.assertIsInstance(distribution, UniformProbabilityDistribution)
        self.assertEqual(distribution.parameters.lower_bound, 1.5)
        self.assertEqual(distribution.parameters.upper_bound, 2.5)
        self.assertIs(
            factory.adapter,
            ProbabilityDistributionSamplerAdapter.NUMPY,
        )


if __name__ == "__main__":
    unittest.main()
