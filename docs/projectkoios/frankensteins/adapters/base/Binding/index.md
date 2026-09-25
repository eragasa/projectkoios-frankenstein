# `Binding`

**Implemented in:** `projectkoios.frankensteins.adapters.base`

`Binding` inherits from `Adapter` and is the nominal base for adapters to
imported or deliberately vendored code dependencies. Concrete bindings own
dependency identity, provenance, API translation, and documented compatibility
behavior as applicable.

A binding does not grant authority to invoke an external application or
service. An integration may contain a binding through composition.
