# Probability distributions and samplers

`ProbabilityDistributionParameters` is the immutable nominal base for parameter
state. `UniformProbabilityDistributionParameters` supplies finite uniform
bounds.

`ProbabilityDistributionSampler` composes parameters with a supported adapter.
`UniformProbabilityDistributionSampler` supports `NumpyAdapter` and delegates
sampling to it. `ProbabilityDistributionSamplerAdapter` is the stable enum used
to select an implementation.

`ProbabilityDistribution` composes one parameters object with a sampler that
references that same object. `UniformProbabilityDistribution` constructs this
composition for the uniform family. `ProbabilityError` reports invalid
parameters, compositions, adapters, and sampling requests.

`UniformProbabilityDistributionSamplerValidationRequest` captures replay and
acceptance controls. `UniformProbabilityDistributionSamplerValidator` consumes
that request and returns an immutable
`UniformProbabilityDistributionSamplerValidation` result.

Fast tests cover contracts and deterministic NumPy conformance. Longer-running
statistical invocations are placed beside consuming distributions, marked
`validation`, and excluded from default check-in verification.
