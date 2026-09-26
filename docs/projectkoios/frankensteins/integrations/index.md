# `projectkoios.frankensteins.integrations`

**Source:** `src/projectkoios/frankensteins/integrations/`

Application-specific boundaries live here. The shared [`BaseExecutor`](base/index.md) defines a nominal typed request/workspace/result boundary while leaving executable selection, authorization, process launch, evidence retention, and output interpretation to concrete integrations.

Maintained integration packages:

- [`quantumespresso`](quantumespresso/index.md)
- [`vasp`](vasp/index.md)

The package initializer does not broadly re-export implementations.
