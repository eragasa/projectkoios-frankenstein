# Implement QE NSCF integration

**Task:** `qe-nscf-integration`

**Status:** Proposed

## Objective

Project and analyze one QE non-self-consistent calculation suitable for an accepted downstream Wannier90 declaration.

## Subtasks

- [Input projection](subtasks/input-projection/index.md)
- [Output analysis](subtasks/output-analysis/index.md)
- [Replay](subtasks/replay/index.md)

## Inputs

- Production SCF saved-state identity.
- Explicit structure, pseudopotential, band-count, occupation, and uniform-k-point declarations.
- QE 7.5 `INPUT_PW` authority.

## Outputs

- Deterministic `calculation='nscf'` input.
- Native NSCF observation and saved-state manifest.
- Replay-capable handler evidence.

## Acceptance

- Prefix, structure, pseudopotential, and saved-state lineage are consistent.
- K-point values, ordering, and weights are explicit.
- Band count is a reviewed input, not inferred from output.

## Non-goals

- Choosing Wannier projections or windows.
- Owning Wannier90 execution.
