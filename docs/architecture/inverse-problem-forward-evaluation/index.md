# Inverse problems through forward evaluation

**Status:** Target reusable architecture reconstructed from historical
interatomic-potential fitting and adapted to a reduced-Hamiltonian inverse
problem.

This module defines the reusable feedback architecture for solving inverse
problems by proposing model parameters, executing a forward evaluator,
preserving raw results, deriving optimizer feedback, and returning that
feedback to the proposing engine.

The historical exemplar is the method of
[Ragasa et al. (2019)](../../references/ragasa-2019-multi-objective-interatomic-potentials.md).
The first target adaptation is the
[`ksdft2effmass` reduced-Hamiltonian problem](../reduced-hamiltonian-inverse-problem/index.md).

- [Architecture](architecture/index.md)
- [Implementation](implementation/index.md)
- [Specifications](specifications/index.md)
- [Testing](testing/index.md)
