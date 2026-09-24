# `MathematicalModelDefinition`

**Implemented in:** `projectkoios.frankensteins.mathematics.models`

Immutable, provenance-bearing definition of one locally evaluable scalar model.

## Fields and contract

The model validates `name`, `output_variable`, historical `source_model_type`,
`kind`, exact ordered `inputs`, unique source variables, `definition_source`,
optional `implementation_source`, `contract_version`, and permanent
`scientific_validation_claimed=False` state. Construction derives `model_id`
from the complete identity payload.

## Properties and methods

- `expression` delegates to the selected `MathematicalModelKind`.
- `unused_required_inputs` exposes retained inputs whose participation flag is
  false.
- `evaluate(values)` requires an exact key set, rejects Booleans, nonnumeric and
  nonfinite values, normalizes signed zero, checks formula denominators, and
  evaluates only the enumerated closed arithmetic branch.
- `to_dict()` serializes identity material and `model_id`.

Evaluation establishes deterministic arithmetic only. It does not establish
units, numerical verification, physical correctness, or scientific validity.
