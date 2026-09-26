# QE uniform-grid NSCF workflow

**Task:** `workflow-qe-uniform-nscf`

**Status:** Proposed

## Objective

Produce the correlated QE non-self-consistent state required by the accepted Wannier90 declaration.

## Subtasks

- [Contracts](subtasks/contracts/index.md)
- [Workflow definition](subtasks/definition/index.md)
- [Replay](subtasks/replay/index.md)

## Dependencies

- Production SCF saved-state manifest.
- [`qe-nscf-integration`](../../../qe/nscf/index.md)
- Uniform k-point and band-count declarations shared with Wannier90.

## Outputs

Completed NSCF result and identified saved-state manifest for `pw2wannier90.x`.

## Acceptance

Structure, pseudopotential, prefix, lineage, k-point order, weights, and band count are mutually consistent.
