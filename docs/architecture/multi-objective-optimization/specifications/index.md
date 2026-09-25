# Multi-objective optimization specifications

```mermaid
stateDiagram-v2
    [*] --> Ready
    Ready --> AwaitingEvaluations: ask
    AwaitingEvaluations --> Ready: tell complete batch
    Ready --> Complete: stopping condition
    Ready --> Checkpointed: checkpoint
    Checkpointed --> Ready: resume
```

- Candidate identifiers **MUST** be unique within a run and stable across restart.
- `ask` **MUST NOT** mutate scientific problem data.
- `tell` **MUST** reject unknown, duplicate, or incompatible evaluations.
- Objective ordering and minimization direction **MUST** be explicit and stable.
- The Ragasa-method implementation **MUST** retain the complete QOI-error vector
  and **MUST NOT** replace Pareto dominance with an undeclared weighted scalar
  objective.
- Initial uniform sampling **MUST** give each independent free parameter its own
  bounded uniform-distribution parameters.
- KDE refinement **MUST** identify the Pareto population and bandwidth policy
  from which the next proposal distribution is constructed.
- Preference-dependent final down-selection **MUST** remain distinct from Pareto
  ensemble construction.
- Random state, algorithm state, iteration index, and accepted evaluation
  identities **MUST** be checkpointed atomically.
- Failed evaluations **MUST** retain candidate identity and failure class.
- Optimizer configuration **MUST NOT** contain calculator paths or structure
  contents.
- Deterministic replay **SHOULD** be possible when given the same checkpoint and
  ordered evaluations.
