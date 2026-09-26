# `UnitCell`

Immutable base composition with public dimensionless and physical column-basis representations:

- `A = [a1 a2 a3]`, a unitless `MatrixQuantity`;
- `H = lattice_parameter A = [h1 h2 h3]`, a length-bearing `MatrixQuantity`;
- `a1`, `a2`, and `a3`, the columns of `A`;
- `h1`, `h2`, and `h3`, the columns of `H`.

`direct_lattice` is a frozen canonical PhysKit `DirectLattice3D`; `lattice_parameter` is the positive physical scale; `atomic_basis` is an exact `AtomicBasis`. The constructor snapshots the supplied lattice.

For a fractional column vector `s`, Cartesian position is `r = H s`. Calculator projections serialize columns of `H` as native lattice vectors.
