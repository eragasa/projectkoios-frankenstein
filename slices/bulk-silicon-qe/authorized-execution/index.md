# Slice: authorized bulk execution

**Status:** Blocked pending verified replay and explicit authorization

## Outcome

Run the accepted bulk-silicon slices with exact operator-supplied resources and retain durable native evidence for every attempted stage.

## Consumed slices

- [SCF convergence](../scf-convergence/index.md)
- [Structural relaxation](../structural-relaxation/index.md)
- [Production SCF and NSCF](../production-scf-nscf/index.md)
- [QE-to-Wannier90 interface](../qe-wannier-interface/index.md)
- [Wannier localization and validation](../wannier-localization-validation/index.md)

## Gate

Every replay slice is verified, scientific declarations and budgets are accepted, executable and pseudopotential bytes match exact identities, storage is preflighted, and the operator explicitly authorizes the identified run.

## Stop conditions

Stop before launch when identity, input, authorization, capacity, or policy evidence is missing. Earlier successful evidence remains retained when a later stage fails.
