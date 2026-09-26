# `projectkoios.frankensteins.physkit.periodic.unit_cell`

Calculator-neutral periodic structure composition with explicit column-vector semantics. `UnitCell` owns `A = [a1 a2 a3]`, physical `H = lattice_parameter A = [h1 h2 h3]`, and an ordered `AtomicBasis`.

`ConventionalUnitCell` and `PrimitiveUnitCell` are nominal subtypes; the distinction is not inferred from geometry or atom count. `UnitCellJsonSerializer` and `UnitCellJsonDeserializer` preserve that declared subtype through reviewed JSON without dynamic imports.

This PhysKit-shaped overlay module is an extraction candidate for PhysKit. Calculator-specific weights, magnetic moments, constraints, and pseudopotential selections remain absent.
