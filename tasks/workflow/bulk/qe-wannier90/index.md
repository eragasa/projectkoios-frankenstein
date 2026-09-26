# Compose bulk QE-to-Wannier90 workflow

**Task:** `workflow-bulk-qe-wannier90`

**Status:** Active planning

## Objective

Compose accepted QE and Wannier90 child workflows into the ordered bulk-silicon slices defined by the active plan.

## Subtasks

- [Accept declarations](declarations/index.md)

## Consumed module tasks

- [QE integration tasks](../../../qe/index.md)
- [QE workflow tasks](../../qe/index.md)
- [Wannier90 integration tasks](../../../wannier/index.md)
- [Wannier90 workflow tasks](../../wannier/index.md)

## Outputs

A parent definition with explicit child correlation, fork/join dependencies, bounded scientific re-entry, preserved failures, and exactly one terminal outcome.

## Acceptance

- The parent stores identifiers rather than native mutable state in markings.
- NSCF and Wannier preprocessing may proceed independently and join before conversion.
- Successful child evidence survives later failure.
- Execution and persistence remain external effects.

## Non-goals

- Duplicating integration behavior.
- Treating JSON presentation as authoritative workflow state.
