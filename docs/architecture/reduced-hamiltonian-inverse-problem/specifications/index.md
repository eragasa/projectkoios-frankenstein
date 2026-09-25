# Reduced-Hamiltonian inverse-problem specifications

- The experiment **MUST** begin from one qualified immutable Wannier parent and
  **MUST** preserve its identity through both reduction routes.
- Spectral and operator routes **MUST** use the same frozen tight-binding model
  class, parameter domain, physical branch, representation conventions, and
  training/withheld partition.
- A candidate **MUST** identify one model class, one route, and one complete
  immutable parameter vector admitted by that class.
- Parameter identity, units, bounds, symmetry relations, orbital ordering,
  neighbor range, lattice convention, Fourier convention, spin convention, and
  energy zero **MUST** be explicit.
- Every independently initialized parameter **MUST** have its own probability-
  distribution parameters object.
- Candidate evaluation **MUST NOT** rerun Quantum ESPRESSO or Wannier90. It
  **MUST** consume the already qualified reference dataset.
- One shared forward-evaluator implementation **SHOULD** calculate both spectral
  and aligned-operator observations for candidates from either route.
- The spectral results handler **MUST** send only frozen spectral training
  feedback to the spectral optimizer.
- The operator results handler **MUST** send only frozen operator training
  feedback to the operator optimizer.
- Each route result **MUST** retain both primary observations and cross-
  evaluation under the other criterion.
- The two optimizer states, random states, candidate lineages, stopping rules,
  and checkpoints **MUST** remain separately identified.
- The model-class hierarchy and order of permitted relaxations **MUST** be
  frozen before fitting results are inspected.
- The reference dataset **MUST** bind the converged Kohn--Sham parent, validated
  Wannier Hamiltonian, training/withheld partition, representation, units,
  gauge, energy reference, and artifact provenance.
- The alignment domain, direction, admissible group, symmetry restrictions,
  conditioning policy, and optimization procedure **MUST** be explicit.
- Spectral and operator objective definitions, weights, normalizations, and
  tolerances **MUST** be frozen before route comparison.
- The compatibility analyzer **MUST NOT** update either route optimizer.
- A jointly admissible candidate **MUST** be one exact candidate satisfying both
  criteria; two separately fitted candidates **MUST NOT** be represented as a
  common Hamiltonian.
- A distance between selected route models **MUST** be described as a measured
  route difference, not automatically as separation of the full admissible
  sets.
- Training observations **MAY** update only their owning route optimizer.
  Withheld observations **MUST NOT** update either optimizer.
- Failed candidates **MUST** retain route, candidate, model-class, parameter,
  and classified-failure identities.
- Finite search failure **MUST NOT** be represented as proof that admissible sets
  are disjoint or have positive global separation.
- Model-reduction error, numerical error, reference-parent error, optimization
  error, and representation/alignment error **MUST** remain distinguishable.
- Software verification **MUST NOT** be represented as a completed bulk-silicon
  fit, numerical verification, scientific validation, or conference result.
