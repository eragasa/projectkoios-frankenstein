# `UniformProbabilityDistributionSampler`

Uniform sampler composed from `UniformProbabilityDistributionParameters` and a
supported adapter. `supported_adapters` currently contains `NumpyAdapter`.
`sample` delegates closed-open uniform sampling to that binding.
