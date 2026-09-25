# `ExternalMathematicalModelDeclaration`

**Implemented in:** `projectkoios.frankensteins.mathematics.models`

Provenance-bearing declaration for a model selected by evidence but delegated
to an external backend.

The class validates `name`, `source_model_type`, `backend_model`, unique bounded
`species`, exactly one nonempty interaction family (`pair_interactions` or
ordered `triplet_interactions`), unique bounded `parameter_variables`, unique
bounded bibliographic `references`, exact `definition_source` and
`implementation_source` spans, and `contract_version` `0.1.0`.

Pairs represent two-body models such as Buckingham. Ordered triplets represent
many-body declarations such as Tersoff, where element order is semantically
significant. References are interpretive support serialized with the model;
they never replace its exact source evidence or make a validation claim.

`evaluation_supported` and `scientific_validation_claimed` must both remain
`False`. Construction derives `model_id`; `to_dict()` serializes the complete
declaration. The class intentionally provides no `evaluate` method.
