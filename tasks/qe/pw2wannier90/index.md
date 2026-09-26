# Implement `pw2wannier90.x` integration

**Task:** `qe-pw2wannier90-integration`

**Status:** Proposed

## Objective

Convert one correlated QE NSCF state and Wannier90 `.nnkp` declaration into identified native interface artifacts.

## Subtasks

- [Input projection](subtasks/input-projection/index.md)
- [Execution boundary](subtasks/execution/index.md)
- [Output analysis](subtasks/output-analysis/index.md)
- [Replay](subtasks/replay/index.md)

## Inputs

- QE NSCF saved-state manifest.
- Wannier90 `.nnkp` identity.
- Reviewed converter input and exact executable identity.

## Outputs

- Captured streams and execution record.
- Declared `.amn`, `.mmn`, `.eig`, and other accepted-mode artifacts with roles, hashes, and sizes.

## Acceptance

- Structure, prefix, k-point ordering, band count, and Wannier-function count agree across inputs.
- Missing, mismatched, oversized, symbolic-link, or malformed required artifacts fail closed.
- QE-specific converter behavior remains under the QE integration.

## Non-goals

- Wannier localization.
- Treating file presence as scientific validation.
