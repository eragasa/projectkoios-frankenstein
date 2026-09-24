# `MathematicalModelKind`

**Implemented in:** `projectkoios.frankensteins.mathematics.models`

`StrEnum` of the only locally supported arithmetic forms:

- `IDENTITY`: `value`
- `NEGATION`: `-value`
- `CUBIC_BULK_MODULUS`: `(c11 + 2 * c12) / 3`
- `TETRAGONAL_SHEAR_MODULUS`: `(c11 - c12) / 2`
- `DEFECT_FORMATION_ENERGY`: defect energy relative to a bulk per-atom energy
- `SURFACE_ENERGY`: two-surface slab excess energy divided by `a1 * a2`

`expression` returns a descriptive closed-form string. `input_contract`
returns ordered `(alias, participates_in_expression)` pairs. Bulk and shear
contracts intentionally require an unused `c44` input to preserve historical
behavior.
