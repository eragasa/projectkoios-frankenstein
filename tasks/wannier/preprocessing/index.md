# Implement Wannier90 preprocessing support

**Task:** `wannier-preprocessing-integration`

**Status:** Proposed

## Objective

Support identified `wannier90.x -pp` input/output behavior without owning parent workflow ordering.

## Subtasks

- [`.nnkp` artifact contract](subtasks/nnkp-artifact/index.md)
- [Preprocessing replay](subtasks/replay/index.md)

## Outputs

Retained `.nnkp`, streams, execution record, and diagnostics.

## Acceptance

Executable identity and `.win` identity are verified; `.nnkp` k-point and neighbor evidence remains native and correlated.
