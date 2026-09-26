# Slice: production SCF and uniform-grid NSCF

**Status:** Proposed

## Outcome

Produce a clean production SCF reference and a correlated uniform-grid NSCF saved state for the accepted relaxed structure.

## Consumed tasks

- [QE saved-state evidence](../../../tasks/qe/saved-state-evidence/index.md)
- [QE NSCF integration](../../../tasks/qe/nscf/index.md)
- [QE post-relaxation confirmation workflow](../../../tasks/workflow/qe/post-relaxation-confirmation/index.md)
- [QE production SCF workflow](../../../tasks/workflow/qe/production-scf/index.md)
- [QE NSCF workflow](../../../tasks/workflow/qe/nscf/index.md)

## Demonstration

Replay post-relaxation confirmation, production SCF, and NSCF while preserving exact structure, pseudopotential, k-point, band-count, and saved-state lineage.

## Gate

Production evidence is independent of convergence workspaces and the NSCF uniform mesh matches the declared downstream Wannier contract.
