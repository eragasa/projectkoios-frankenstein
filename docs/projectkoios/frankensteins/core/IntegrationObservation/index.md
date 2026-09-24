# `IntegrationObservation`

**Implemented in:** `projectkoios.frankensteins.core`

Calculator-neutral envelope for one integration's versioned JSON payload.

## Fields

- `integration` is a bounded lowercase integration identifier.
- `contract_version` is nonempty and at most 64 characters.
- `payload_json` must decode to a JSON object and must already equal the core
  canonical JSON encoding.

## Construction and serialization

`from_payload(...)` canonicalizes a dictionary before constructing the value.
`to_dict()` returns `integration`, `contract_version`, and the decoded payload.

Canonical payload enforcement makes recipe identity independent of formatting
or dictionary insertion order.
