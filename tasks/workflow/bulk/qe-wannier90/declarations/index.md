# Accept bulk QE-to-Wannier90 declarations

**Subtask:** `workflow-bulk-qe-wannier90-declarations`

**Parent task:** [Compose bulk QE-to-Wannier90 workflow](../index.md)

**Status:** Active; human decisions required

## Objective

Bind every scientific choice required by downstream slices without granting execution authority.

## Outputs

Reviewed declarations for structure, relaxation role, convergence policies, pseudopotential, spin/SOC, Wannier subspace, uniform mesh, bands, windows, validation policy, executables, and bounded resources.

## Acceptance

Every required choice is explicit and typed; concrete resources have cryptographic identities; undecided values block only dependent tasks; scientific records contain no machine-local absolute paths.

## Non-goals

Executing calculators or inferring scientific policy from output.
