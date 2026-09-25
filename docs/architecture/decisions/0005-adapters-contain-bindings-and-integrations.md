# Decision 0005: Adapters contain bindings and integrations

## Status

Accepted.

## Context

The reconstruction code needs separate terms for two boundaries that were both
previously called adapters or engines. PyFlamestk, PyPosPack, PyGithub, and
similar packages are imported or selectively vendored code dependencies.
LAMMPS, VASP, GitHub, and similar calculators or services are external systems
with distinct effect authority.

The `projectkoios.frankensteins` namespace is also intended to incubate modules
that can be picked and pulled into the distributed `projectkoios` namespace.
Repository names need to remain stable when a capability owns both boundary
roles.

## Decision

`Adapter` is the nominal containing base class. `Binding` and `Integration` are
separate base-class roles below it.

- A binding adapts an imported or deliberately vendored code dependency.
- An integration adapts an external application or service.
- An integration may contain a binding through composition.
- No generic `adapt()` method is implied by nominal adapter membership.

Provider repositories use capability names such as `projectkoios-github` and
`projectkoios-lammps`. Architectural role is expressed by import namespaces,
not encoded into repository names.

The Frankenstein namespace mirrors the target namespace. For example:

```text
projectkoios.frankensteins.adapters.bindings.pypospack
    -> projectkoios.adapters.bindings.pypospack

projectkoios.frankensteins.adapters.integrations.lammps
    -> projectkoios.adapters.integrations.lammps
```

Migration removes the incubation segment without renaming domain classes or
redesigning their inheritance. Shared package initializers do not aggregate all
implementations; only leaf facades or explicit composition roots may expose a
curated API.

## Consequences

- Historical PyFlamestk and PyPosPack code-facing reconstruction moves toward
  binding namespaces rather than engine namespaces.
- LAMMPS and VASP remain integrations.
- A GitHub capability may own a PyGithub binding and GitHub integration in one
  repository while keeping their classes distinct.
- Existing uses of "adapter" for other architectural boundaries are not
  automatically reclassified; binding and integration are two named adapter
  subsets.
- New shared base classes still require an explicit architecture discussion
  before implementation.
- Tests and documentation mirror intended pick-and-pull package paths.

## Alternatives considered

### Encode adapter kind in repository names

Rejected. Names such as `projectkoios-integration-github` couple repository
identity to one role even when the capability also owns a binding.

### Use `external` as the repository family

Rejected. "External" describes contribution or governance ownership
ambiguously and does not distinguish a dependency binding from an application
integration.

### Combine bindings and integrations

Rejected. Dependency API adaptation and external effect authority require
different contracts, tests, and evidence.
