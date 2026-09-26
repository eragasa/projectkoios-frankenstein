# Implement VASP structural-relaxation integration

**Task:** `vasp-structural-relaxation-integration`

**Status:** Proposed

## Objective

Project the generic structural-relaxation request into typed VASP-native INCAR, KPOINTS, and POSCAR declarations with qualified `IBRION`, `ISIF`, termination, and evidence behavior.

## Acceptance

VASP fields remain native; optimizer and cell-degree mappings carry explicit fidelity and non-equivalence qualifications.

## Dependency

The calculator-neutral input wrapper is maintained. This task does not block the active QE vertical slice.
