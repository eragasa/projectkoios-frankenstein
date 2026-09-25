# QOI evaluation

**Status:** Target module

This module turns simulation results into physical observations while preserving
the distinction between observations and optimization losses.

```mermaid
flowchart LR
    Q[Material-property QOIs] --> C[CPN workflow mapping]
    C --> R[Simulation results]
    R --> V[Material-property observations]
    V --> T[Objective transform]
```

- [Architecture](architecture/index.md)
- [Implementation](implementation/index.md)
- [Specifications](specifications/index.md)
- [Testing](testing/index.md)
