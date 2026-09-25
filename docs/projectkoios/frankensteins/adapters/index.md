# `projectkoios.frankensteins.adapters`

**Source:** `src/projectkoios/frankensteins/adapters/`

This mirrored incubation namespace owns transfer-ready adapter contracts.
[Adapter base classes](base/index.md) distinguish bindings to imported or
vendored code from integrations with external applications and services.

The namespace is designed to move to `projectkoios.adapters` by removing only
the `frankensteins` segment. Shared namespace levels do not aggregate
implementation classes; callers import from owning modules or deliberate
provider-leaf facades.
