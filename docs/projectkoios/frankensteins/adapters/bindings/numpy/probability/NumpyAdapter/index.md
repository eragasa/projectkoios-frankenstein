# `NumpyAdapter`

A nominal `Binding` to imported NumPy behavior. `sample_uniform` receives
validated bounds, an explicit sample count, and a `random_seed`. The
`sample_independent_uniform` action accepts one bound pair per independent dimension
and returns immutable row-major samples. Both actions create an isolated NumPy legacy
random state without mutating NumPy's global random state.
