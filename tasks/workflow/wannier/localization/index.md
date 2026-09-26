# Wannier90 localization workflow

**Task:** `workflow-wannier-localization`

**Status:** Proposed

## Objective

Join accepted interface artifacts and drive Wannier90 localization through one external handler.

## Subtasks

- [Workflow definition](subtasks/definition/index.md)
- [Replay](subtasks/replay/index.md)

## Dependencies

- [Wannier90 execution](../../../wannier/execution/index.md)
- [Wannier90 output](../../../wannier/output/index.md)
- [`pw2wannier90.x` integration](../../../qe/pw2wannier90/index.md)

## Acceptance

Input identities agree, earlier artifacts survive later failure, and process completion remains distinct from localization convergence.
