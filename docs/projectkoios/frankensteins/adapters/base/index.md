# `projectkoios.frankensteins.adapters.base`

**Source:** `src/projectkoios/frankensteins/adapters/base.py`

This module owns the migration-stable nominal adapter hierarchy:

- `Adapter` contains maintained boundary adapter roles;
- `Binding` identifies adapters to imported or deliberately vendored code; and
- `Integration` identifies adapters to external applications or services.

The classes provide runtime `isinstance` and `issubclass` membership without
inventing a common `adapt()` or `execute()` operation. Concrete adapters define
their own immutable data and narrow behavior. An integration may contain a
binding through composition; neither role inherits from the other.

During pick-and-pull migration this module moves to
`projectkoios.adapters.base` without class renaming or hierarchy redesign.
