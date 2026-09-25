# `Adapter`

**Implemented in:** `projectkoios.frankensteins.adapters.base`

`Adapter` is the common nominal base for maintained boundary adapter roles. It
has no fields and does not define a generic `adapt()` or `execute()` method.
Its purpose is runtime classification through `isinstance` and `issubclass`.

`Binding` and `Integration` inherit from `Adapter`. Additional shared adapter
base classes require an explicit architecture discussion before implementation.
