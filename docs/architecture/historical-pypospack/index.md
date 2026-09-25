# Historical PyPosPack adapter

**Status:** Partially implemented reconstruction module

This module isolates source-bound PyPosPack behavior behind maintained contracts.
Vendored code supplies conformance evidence and is not the domain API.

```mermaid
flowchart LR
    H[Historical configuration and runtime] --> A[Adapter]
    A --> M[Maintained models]
```

- [Architecture](architecture/index.md)
- [Implementation](implementation/index.md)
- [Specifications](specifications/index.md)
- [Testing](testing/index.md)
- [MgO Buckingham source mapping](../pypospack-mgo-buckingham.md)
