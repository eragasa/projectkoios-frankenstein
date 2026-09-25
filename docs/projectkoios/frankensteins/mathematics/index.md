# `projectkoios.frankensteins.mathematics`

**Source:** `src/projectkoios/frankensteins/mathematics/`

This package incubates immutable mathematical definitions extracted from
verified source evidence. Implementations are imported from their defining
modules rather than broadly re-exported by a package facade.

- [`models`](models/index.md) records reconstructed mathematical-model evidence.
- [`probability`](probability/index.md) defines probability distributions and
  parameterized sampler contracts.

Only enumerated, closed arithmetic is locally evaluable. Calculator-backed
models remain explicit, evaluation-disabled declarations. Numerical sampling is
provided through external dependency bindings.
