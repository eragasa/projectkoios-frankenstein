# `UnitCellChargeConstraintCompiler`

`compile` selects one named structure from a material system, reads its species
multiplicities and total-charge target, divides all coefficients and the target
by their common multiplicity, and returns an immutable stoichiometric equality.
