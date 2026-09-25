# `UnitCellDeclaration`

Mutable authoring state containing a PhysKit `direct_lattice` and
`species_multiplicities`. The `reciprocal_lattice` property delegates derivation
to PhysKit's `ReciprocalLattice3D`. The `charge` property accepts the declarative
unit-cell total-charge target. The declaration is compiled before execution and
is not itself an execution data object.
