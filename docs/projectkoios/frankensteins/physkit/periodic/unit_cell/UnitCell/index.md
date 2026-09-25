# `UnitCell`

Immutable composition with public `primitive_lattice`, `lattice_parameter`, and `atomic_basis` fields. `primitive_lattice` is the dimensionless matrix `A` represented by a PhysKit `DirectLattice3D`; `lattice_parameter` is a positive PhysKit `ScalarQuantity` with length dimensionality; `atomic_basis` is an exact `AtomicBasis`.

The physical cell matrix is `H = lattice_parameter × A`. Atomic positions remain dimensionless fractional coordinates. This contract does not choose a conventional cell, normalize sites into `[0, 1)`, select pseudopotentials, or define calculator inputs.
