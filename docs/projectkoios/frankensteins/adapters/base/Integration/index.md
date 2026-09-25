# `Integration`

**Implemented in:** `projectkoios.frankensteins.adapters.base`

`Integration` inherits from `Adapter` and is the nominal base for adapters to
external applications or services. Concrete integrations own their explicit
effect, request, result, workspace, authentication, executable, or external
version boundaries as applicable.

An integration may contain a compatible `Binding` through composition. It does
not inherit from `Binding`, and the base class supplies no implicit execution
behavior.
