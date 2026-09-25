# Colored-Petri-net visualization

**Status:** Target module; generic renderer ownership belongs to the future
`projectkoios-cpn` owner

The visualizer makes a CPN definition and its current execution evidence
inspectable without changing workflow state.

```mermaid
flowchart LR
    D[CPN definition] --> V[Read-only visualizer]
    M[Current marking] --> V
    E[Enablement and firing evidence] --> V
    A[Scientific annotations] --> V
    V --> R[Interactive and static views]
```

- [Architecture](architecture/index.md)
- [Implementation](implementation/index.md)
- [Specifications](specifications/index.md)
- [Testing](testing/index.md)
