# `ObservedSetting`

**Implemented in:** `projectkoios.frankensteins.core`

Immutable record of one setting observed in retained source evidence.

## Fields and invariants

- `key` follows the core bounded-name grammar.
- `values` contains between 1 and 32 nonempty strings, each at most 512
  characters.
- `evidence_path` is a normalized relative POSIX path.
- `line_number` is in `1..1_000_000`.

`to_dict()` serializes `values` as an ordered JSON array. The class preserves
what was observed; it does not interpret scientific meaning or authorize use.
