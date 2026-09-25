"""Probability-distribution composition for the historical Mg charge parameter."""

from __future__ import annotations

from dataclasses import dataclass

from projectkoios.frankensteins.mathematics.probability import (
    ProbabilityDistributionSamplerAdapter,
    UniformProbabilityDistribution,
    UniformProbabilityDistributionParameters,
)

# Bounds are derived from pinned source path
# examples/lmps_MgO_serial_uniform/pyposmat.potential,
# SHA-256 bb6bb6461468c96012acfa298bd1fc473d771d3ce82f1c4effed662e9ffa1e1d.
_MG_CHARGE_LOWER_BOUND = 1.5
_MG_CHARGE_UPPER_BOUND = 2.5


@dataclass(frozen=True, slots=True)
class MgOChargeProbabilityDistributionFactoryObject:
    """Create the Mg charge distribution consumed by the historical sampler."""

    adapter: ProbabilityDistributionSamplerAdapter = (
        ProbabilityDistributionSamplerAdapter.NUMPY
    )

    def create(self) -> UniformProbabilityDistribution:
        """Create the source-conformant uniform Mg charge distribution."""

        return UniformProbabilityDistribution(
            UniformProbabilityDistributionParameters(
                lower_bound=_MG_CHARGE_LOWER_BOUND,
                upper_bound=_MG_CHARGE_UPPER_BOUND,
            ),
            adapter=self.adapter,
        )


__all__ = ["MgOChargeProbabilityDistributionFactoryObject"]
