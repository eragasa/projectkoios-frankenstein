# Implement QE structural-relaxation integration

**Task:** `qe-structural-relaxation-integration`

**Status:** Active; card-based input projection is maintained, output evidence and scientific policy remain open

## Objective

Add the minimum QE-native projection and output analysis required by the accepted bulk structural-relaxation workflow.

## Subtasks

- [Input projection](subtasks/input-projection/index.md) — closed
- [Output analysis](subtasks/output-analysis/index.md)
- [Relaxed structure](subtasks/relaxed-structure/index.md)
- [Replay](subtasks/replay/index.md)

## Inputs

- Calculator-neutral relaxation request.
- Accepted `relax` or `vc-relax` policy.
- QE 7.5 `INPUT_PW` authority.
- Exact species and pseudopotential declarations.

## Outputs

- Deterministic `pw.x` input projection.
- Native completion, force, stress, pressure, step, final-cell, and final-position observations supported by the accepted format contract.
- Immutable relaxed-structure result with artifact provenance.

## Acceptance

- `&CONTROL`, `&IONS`, and `&CELL` fields are explicit rather than hidden defaults.
- Final structure extraction fails closed on incomplete or malformed output.
- Native units and raw output identity are retained.

## Current implementation evidence

- `src/projectkoios/frankensteins/integrations/quantumespresso/pw_dft_relaxation/`
- `tests/projectkoios/frankensteins/integrations/quantumespresso/pw_dft_relaxation/`

The maintained projection uses typed QE namelist and data-card declarations. Test values exercise the boundary and are not an accepted bulk-silicon relaxation policy.

## Non-goals

- Owning parent workflow retries or convergence loops.
- Treating exit status as relaxation convergence.
