# `RecipeWarning`

**Implemented in:** `projectkoios.frankensteins.core`

A structured limitation or inconsistency attached to a reconstructed recipe.

## Fields and invariants

- `code` follows the core bounded-name grammar.
- `evidence_paths` contains 1 to 64 normalized relative paths.
- `detail` is nonempty and at most 1,000 characters.

`to_dict()` emits the code, ordered evidence paths, and human-readable detail.
Warnings retain limitations instead of silently repairing historical evidence.
