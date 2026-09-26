# Calculator-selectable structural-relaxation input wrapper

**Task:** `workflow-dft-structural-relaxation-input-wrapper`

**Status:** Closed — input-selection boundary implemented

## Objective

Select one installed QE, VASP, or ABINIT integration by stable value identity while preserving each calculator's native input organization.

## Subtasks

- [Generic request contracts](subtasks/contracts/index.md)
- [Backend and enum descriptions](subtasks/descriptions/index.md)
- [Integration selection](subtasks/integration-selection/index.md)

## Outputs

- Calculator-neutral relaxation scope, sampling, and convergence declarations.
- Reviewed backend descriptions for QE namelists/cards, VASP native files, and ABINIT datasets/variables.
- A nominal integration registry and input wrapper selected by `CalculatorIntegrationId` value.

## Acceptance

- Backend descriptions do not route dynamically or claim algorithm equivalence.
- Integration identities are immutable values, not global singleton constants.
- Only installed input projections may enter the registry.
- VASP and ABINIT remain described but unimplemented until their native integrations exist.

## Implementation evidence

- `src/projectkoios/frankensteins/applications/pw_dft_relaxation/`
- `tests/projectkoios/frankensteins/applications/pw_dft_relaxation/`

## Non-goals

- Calculator execution or output analysis.
- Inventing one shared pseudo-input syntax.
- Accepting numerical relaxation policy for bulk silicon.
