# Repair the preserved LAMMPS reconstruction

**Task:** `lammps-reconstruction`

**Status:** Deferred

**Branch:** `dev/lammps-reconstruction`

**Recovery commit:** `2b99603`

## Objective

Replace obsolete `core` and `evidence` dependencies, modernize ownership, and restore verification without executing historical source or LAMMPS.

## Acceptance

- Recovered LAMMPS tests collect and pass.
- Leaf-module imports replace broad package façades.
- Provenance and source boundaries remain exact.
- Full repository verification passes before merge.

## Next safe action

Repair the leaf-module contracts on the isolated branch when this task is promoted to active.
