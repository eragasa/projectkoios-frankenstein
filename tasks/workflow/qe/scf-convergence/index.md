# QE SCF convergence workflow

**Task:** `workflow-qe-scf-convergence`

**Status:** Active evidence repair; workflow control is maintained

## Objective

Compose `dft_pw_scf` children into bounded k-point, cutoff, and joint-confirmation campaigns.

## Child tasks

- [K-point convergence](subtasks/k-points/index.md)
- [Wavefunction-cutoff convergence](subtasks/wavefunction-cutoff/index.md)
- [Joint confirmation](subtasks/joint-confirmation/index.md)

## Inputs

- Initial structure and exact QE resource identities.
- Axis and joint convergence policies.

## Outputs

- Accepted mesh and cutoff settings with evidence; or
- one bounded exhaustion or failure outcome.

## Acceptance

- Adaptive extension adds tokens and child requests without changing topology.
- Operational retry remains separate from scientific extension.
- Accepted settings cite retained native observations and policy identity.

## Non-goals

- Structural relaxation.
- Band or Wannier convergence.
