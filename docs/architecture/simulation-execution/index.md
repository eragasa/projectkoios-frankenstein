# Simulation execution

**Status:** Target module

This module safely turns simulation task descriptions into classified results
and provenance-bearing artifacts. It owns process authority but no scientific
objective semantics.

```mermaid
flowchart LR
    B[Enabled CPN binding] --> E[Execution boundary]
    E --> C[Calculator]
    C --> R[External-output binding]
```

- [Architecture](architecture/index.md)
- [Implementation](implementation/index.md)
- [Specifications](specifications/index.md)
- [Testing](testing/index.md)
