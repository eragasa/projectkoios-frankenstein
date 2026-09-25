# `Atom`

Immutable atom with public `symbol` and `position_fractional` fields. `symbol` is a chemical element symbol. `position_fractional` is a three-component PhysKit `VectorQuantity` whose unit is exactly `Unitless`; PhysKit owns finite immutable binary64 storage.

Weights, `magmom`, force constraints, and calculator-specific labels are not yet represented.
