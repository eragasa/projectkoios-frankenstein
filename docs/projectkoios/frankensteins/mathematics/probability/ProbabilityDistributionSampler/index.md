# `ProbabilityDistributionSampler`

Sampler behavior composed from immutable `parameters` and an externally backed
`adapter`. Each subclass declares immutable `supported_adapters` and implements
`sample` by delegating to its selected adapter.
