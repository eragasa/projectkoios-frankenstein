# `MathematicalModelCatalog`

**Implemented in:** `projectkoios.frankensteins.mathematics.models`

Ordered model collection selected by one exact component revision and example.

## Invariants

- `source_component`, exact Git `source_revision`, and normalized relative
  `source_example_root` are mandatory.
- `models` is a nonempty tuple of at most 1,000 local definitions.
- `external_models` is a tuple of at most 1,000 external declarations.
- Local names, external names, and local output variables are unique; local and
  external names cannot overlap.
- `contract_version` is exactly `0.1.0`.

Construction derives `catalog_id` from the complete ordered identity payload.
`model(name)` returns a local model or raises `KeyError`. `to_dict()` emits the
ordered local and external models plus `catalog_id`.
