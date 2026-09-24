# `MathematicalModelInput`

**Implemented in:** `projectkoios.frankensteins.mathematics.models`

One ordered input binding for a reconstructed model.

## Fields

- `alias` is the name used by the closed arithmetic implementation.
- `source_variable` is the exact historical variable supplied by callers.
- `participates_in_expression` records whether the required input is actually
  used by the formula.

Both names follow the mathematical identifier grammar. The participation flag
must be a real Boolean. `to_dict()` preserves all three fields, including
historically required but unused inputs.
