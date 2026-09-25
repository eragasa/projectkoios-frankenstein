# Inverse-problem forward-evaluation specifications

- The composition root **MUST** wire one optimization engine, one functional
  evaluator, one results handler, and identified immutable reference evidence.
- The results handler **MUST** return feedback to the same optimization-engine
  instance that proposed the evaluated candidate.
- The optimization engine **MUST** own candidate proposal, sampling policy,
  random state, update policy, stopping policy, and checkpoints.
- A parameter sampler **MUST** accept probability-distribution definitions and
  **MUST NOT** own the scientific forward model, reference evidence, objective
  definitions, or external calculators.
- Every independently sampled dimension of an initial uniform proposal **MUST**
  have its own `UniformProbabilityDistributionParameters`.
- The functional evaluator **MUST** return raw observations without mutating
  optimizer state.
- A candidate **MUST** identify its parameterized-model class and complete
  immutable parameter values.
- Reference evidence **MUST** be qualified outside the candidate loop and retain
  source-model, software, numerical-policy, artifact, and provenance identities.
- The results handler **MUST** preserve raw candidate and reference observations
  before deriving residuals, losses, rankings, or optimizer feedback.
- Fixed and dependent parameters **MUST** be resolved before forward evaluation.
- Constraint, construction, numerical, external-execution, observation,
  objective, and optimizer-update failures **MUST** remain distinguishable.
- Configuration **MUST** select concrete implementations explicitly and produce
  replayable resolved state.
- Passing software tests **MUST NOT** be represented as numerical verification,
  reference qualification, scientific validation, or model acceptance.

Scientific specializations add stricter contracts:

- historical interatomic-potential behavior is specified by the
  [potential-optimization module](../../potential-optimization/specifications/index.md);
- the target tight-binding behavior is specified by the
  [reduced-Hamiltonian module](../../reduced-hamiltonian-inverse-problem/specifications/index.md).
