# Validation architecture

Validation converts an explicit subject and criteria into bounded evidence.
Malformed requests and execution failures remain distinct from valid requests
whose subjects fail one or more criteria.

```mermaid
flowchart LR
    S[Subject] --> R[Validation request]
    C[Criteria and replay controls] --> R
    R --> V[Domain validator]
    V --> E[Immutable validation evidence]
    E --> P[Consumer policy or test assertion]
```

The framework does not define scientific criteria, severity, persistence,
scheduling, or human acceptance. Those remain with the consuming domain.
