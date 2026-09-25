# PyFlamestk MgO examples architecture

The historical examples express one related MgO Buckingham problem through
several sampling, execution, analysis, and regression workflows. Treating each
script as an independent engine would duplicate scientific meaning and preserve
historical orchestration as architecture.

```mermaid
flowchart TD
    E[Exact source example] --> R[Provenance-bound Frankenstein recipe]
    R --> B[Shared MgO Buckingham problem]
    R --> V{Scenario variation}
    V --> U[Uniform sampling]
    V --> K[KDE sampling]
    V --> F[From-file evaluation]
    V --> I[Iterative Pareto sampling]
    V --> X[Serial or MPI execution profile]
    V --> A[Analysis or regression scenario]
```

The existing Frankenstein reconstruction is the mandatory source boundary. It
captures source identities, observed settings, calculator intents, structures,
mathematical models, warnings, and execution-disabled status. A worked example
uses those reconstructed facts to configure maintained domain models; it does
not reread or execute the historical entrypoint.

Scientifically equivalent examples share one potential problem and reusable CPN
fragment templates. Sampling method is optimizer policy. Serial versus MPI is
execution policy. Postprocessing and regression are observation/replay concerns.
Content-identical source trees remain distinct provenance bindings but may share
the same maintained scenario template.
