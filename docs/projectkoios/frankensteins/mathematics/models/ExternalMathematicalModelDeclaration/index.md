# `ExternalMathematicalModelDeclaration`

**Implemented in:** `projectkoios.frankensteins.mathematics.models`

Provenance-bearing declaration for a model selected by evidence but delegated
to an external backend.

The class validates `name`, `source_model_type`, `backend_model`, unique bounded
`species`, valid and unique `pair_interactions`, unique bounded
`parameter_variables`, exact `definition_source` and `implementation_source`
spans, and `contract_version` `0.1.0`.

`evaluation_supported` and `scientific_validation_claimed` must both remain
`False`. Construction derives `model_id`; `to_dict()` serializes the complete
declaration. The class intentionally provides no `evaluate` method.
