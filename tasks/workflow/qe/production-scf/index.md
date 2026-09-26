# QE production SCF workflow

**Task:** `workflow-qe-production-scf`

**Status:** Proposed

## Objective

Create a clean SCF reference on the accepted relaxed structure for downstream NSCF work.

## Subtasks

- [Saved-state correlation](subtasks/saved-state-correlation/index.md)

## Dependencies

- Post-relaxation confirmation.
- Maintained `dft_pw_scf` workflow.
- [`qe-saved-state-evidence`](../../../qe/saved-state-evidence/index.md)

## Outputs

Converged SCF result and identified QE saved-state manifest.

## Acceptance

Production evidence is independent of convergence workspaces and preserves exact structure, sampling, executable, pseudopotential, input, output, and saved-state identities.
