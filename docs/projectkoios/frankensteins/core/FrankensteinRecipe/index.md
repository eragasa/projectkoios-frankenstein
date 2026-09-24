# `FrankensteinRecipe`

**Source:** `src/projectkoios/frankensteins/core.py`

Immutable, content-addressed reconstruction result.

## Fields

- `engine_name`: bounded engine identity.
- `source_component`: upstream component identity.
- `source_repository_url`: bounded HTTPS upstream repository URL.
- `source_revision`: exact Git commit SHA-1.
- `source_tree`: exact Git tree SHA-1.
- `source_example_root`: selected repository-relative example root.
- `source_license_path` and `source_license_sha256`: license identity.
- `source_files`: sorted, unique `SourceFileEvidence` values.
- `settings`, `integrations`, `mathematical_models`, and `warnings`: immutable
  reconstructed observations.
- `execution_authorized`: always false.
- `recipe_id`: derived stable identity.

## Methods

- `_identity_dict()` returns contract `projectkoios.frankenstein-recipe` version
  `0.3.0` identity material.
- `to_dict()` adds `recipe_id`.
- `to_json()` returns deterministic formatted JSON with a final newline.

The mathematical-model catalog must carry the same component, revision, and
example root. A recipe does not authorize calculator execution or claim
scientific validity.
