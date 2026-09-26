# Bind retained QE SCF convergence evidence

**Task:** `qe-retained-scf-convergence-evidence`

**Status:** Active

## Objective

Replace demonstration-only convergence inputs with independently retained QE observations carrying exact artifact and resource identities.

## Subtasks

- [Evidence schema](subtasks/schema/index.md)
- [Retained declarations](subtasks/declarations/index.md)
- [Replay verification](subtasks/replay/index.md)

## Inputs

- Existing retained QE 7.5 grid outputs under ignored workspace storage.
- Maintained QE stdout/stderr analysis.
- Accepted evidence schema and scientific qualifications.

## Outputs

- Data-only evidence declarations with observation, artifact hash, byte size, executable identity, pseudopotential identity, structure identity, and diagnostics.
- Replay tests that do not generate fixtures from asserted expectations.

## Dependencies

- Accepted structure and convergence-policy identities.

## Acceptance

- Synthetic control fixtures are not presented as scientific evidence.
- Every normalized energy cites native output bytes.
- Evidence declares that total-energy convergence does not establish band or Wannier convergence.

## Non-goals

- New QE execution.
- Cross-calculator claims using structurally misaligned VASP evidence.
