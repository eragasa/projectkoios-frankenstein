# Historical PyPosPack adapter specifications

```mermaid
flowchart LR
    P[Pinned source identity] --> V[Vendored bytes]
    V --> A[Adapter behavior]
    A --> M[Maintained model]
    P --> C[Conformance record]
    M --> C
```

- Every source file **MUST** bind to repository, commit, tree, path, Git mode,
  blob identity, SHA-256, byte size, and applicable license.
- Vendored files **MUST** be read from committed Git objects.
- Unmodified files **MUST** remain byte-identical.
- Every derived file **MUST** identify its source blob and local modifications.
- Historical YAML **MUST** be parsed with a loader limited to the exact required
  legacy tag.
- Known source defects **MUST** be rejected or adapted explicitly.
- The adapter **MUST NOT** claim a local repair was made upstream.
- Checkout paths and branch names **MUST NOT** enter durable provenance.
- Conformance **MUST NOT** be reported as numerical verification or scientific
  validation.
