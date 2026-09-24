# `projectkoios.frankensteins.core`

**Source:** `src/projectkoios/frankensteins/core.py`

This module owns generic identity, evidence, warning, integration-payload, and
recipe contracts. It contains no calculator-specific policy.

## Functions

- `canonical_json_bytes(value)` emits sorted, compact UTF-8 JSON with one final
  newline. It is the canonical representation used by content identities.
- `stable_id(kind, value)` validates a lowercase identity kind and returns
  `<kind>:sha256:<digest>` over `canonical_json_bytes(value)`.
- `json_payload(value)` returns canonical JSON text for an integration payload.
- `_relative_path(value, field_name)` is the shared internal validator for
  normalized, nonempty, relative POSIX paths without `.` or `..` components.

## Classes

- [`SourceFileEvidence`](SourceFileEvidence/index.md)
- [`ObservedSetting`](ObservedSetting/index.md)
- [`RecipeWarning`](RecipeWarning/index.md)
- [`IntegrationObservation`](IntegrationObservation/index.md)
- [`FrankensteinRecipe`](FrankensteinRecipe/index.md)

## Validation vocabulary

Internal regular expressions constrain SHA-256 digests, exact Git SHA-1
revisions, and bounded lowercase names. All public model classes are frozen
dataclasses. Serialization converts tuples to JSON arrays but never includes
machine-local repository paths.
