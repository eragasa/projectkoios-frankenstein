# `projectkoios.frankensteins.physkit.periodic.unit_cell`

Minimal calculator-neutral periodic structure composition. `UnitCell` contains one dimensionless PhysKit `DirectLattice3D` matrix `A`, one explicit physical `ScalarQuantity` lattice parameter, and one `AtomicBasis`. The physical cell matrix is `H = lattice_parameter × A`. `AtomicBasis` contains ordered `Atom` values. Each atom contains its chemical symbol and an explicitly unitless PhysKit `VectorQuantity` of fractional coordinates.

This PhysKit-shaped overlay module is the initial extraction candidate for PhysKit. POSCAR and Quantum ESPRESSO structure adapters should consume this object rather than owning independent structures. Calculator-specific weights, magnetic moments, constraints, and pseudopotential selections are deliberately absent until their ownership is specified.
