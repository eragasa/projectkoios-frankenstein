# Adapter implementation

**Incubation namespace:** `projectkoios.frankensteins.adapters`

**Migration namespace:** `projectkoios.adapters`

The proposed base-class and provider layout is:

```mermaid
classDiagram
    class Adapter
    class Binding
    class Integration
    class PyGithubBinding
    class GitHubIntegration
    class PypospackBinding
    class LammpsIntegration

    Adapter <|-- Binding
    Adapter <|-- Integration
    Binding <|-- PyGithubBinding
    Binding <|-- PypospackBinding
    Integration <|-- GitHubIntegration
    Integration <|-- LammpsIntegration
    GitHubIntegration o-- PyGithubBinding
```

The corresponding package dependencies are:

```mermaid
flowchart TD
    A[adapters base classes]
    PB[adapters.bindings.pypospack] --> A
    PG[adapters.bindings.pygithub] --> A
    LI[adapters.integrations.lammps] --> A
    GI[adapters.integrations.github] --> A
    GI --> PG
```

A capability repository may contribute more than one leaf namespace. For
example, `projectkoios-github` may publish both
`projectkoios.adapters.bindings.pygithub` and
`projectkoios.adapters.integrations.github`. Shared namespace directories must
remain compatible with Project Koios implicit namespace packaging. A provider
leaf `__init__.py` may act as an intentional facade or composition root; shared
parents do not aggregate every implementation class.

The historical PyFlamestk and PyPosPack reconstruction work moves toward
binding packages because it adapts pinned or vendored code. LAMMPS and VASP
remain integration packages because they represent external scientific
applications. A binding may produce a typed request consumed by an integration,
but it does not execute that application.
