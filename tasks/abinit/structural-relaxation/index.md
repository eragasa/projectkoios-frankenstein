# Implement ABINIT structural-relaxation integration

**Task:** `abinit-structural-relaxation-integration`

**Status:** Proposed

## Objective

Project the generic structural-relaxation request into typed ABINIT-native dataset and input-variable declarations with explicit geometry, optimization, termination, and evidence behavior.

## Acceptance

ABINIT variables remain native; optimizer and cell-degree mappings carry explicit fidelity and non-equivalence qualifications.

## Dependency

The calculator-neutral input wrapper is maintained. This task does not block the active QE vertical slice.
