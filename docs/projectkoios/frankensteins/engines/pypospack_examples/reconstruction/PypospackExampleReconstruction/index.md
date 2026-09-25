# `PypospackExampleReconstruction`

Immutable provenance record for a statically reconstructed PyPosPack example.

## Fields and properties

- `binding`: exact example-engine binding.
- `source_files`: sorted per-file SHA-256 and byte-size evidence.
- `integration`: execution-surface observation.
- `warnings`: explicit non-execution warnings.
- `execution_authorized`: always false.
- `scientific_validation_claimed`: always false.
- `reconstruction_id`: deterministic content identity.
- `engine_name`: bound engine identifier.
- `source_example_root`: bound upstream example path.

`to_dict()` and `to_json()` serialize the reconstruction without including the
local checkout path.
