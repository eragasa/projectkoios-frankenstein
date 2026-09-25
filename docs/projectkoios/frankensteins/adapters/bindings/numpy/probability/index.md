# NumPy probability adapter

`NumpyAdapter` exposes NumPy-backed `sample_uniform` behavior for maintained
probability-distribution samplers. It uses the legacy `RandomState` family found
in pinned PyFlamestk evidence while isolating global random state.
