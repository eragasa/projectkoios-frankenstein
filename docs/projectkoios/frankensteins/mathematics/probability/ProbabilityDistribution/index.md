# `ProbabilityDistribution`

Immutable composition of `parameters` and a configured `sampler`. Construction
requires `sampler.parameters` to be the identical parameters object, preventing
divergent configuration state.
