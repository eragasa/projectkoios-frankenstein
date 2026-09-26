# Slice: Wannier localization and validation

**Status:** Proposed

## Outcome

Produce one identified Wannier localization result and a property-qualified DFT-to-Wannier validation outcome.

## Consumed tasks

- [Wannier90 execution](../../../tasks/wannier/execution/index.md)
- [Wannier90 output](../../../tasks/wannier/output/index.md)
- [Wannier localization workflow](../../../tasks/workflow/wannier/localization/index.md)
- [DFT-to-Wannier validation workflow](../../../tasks/workflow/wannier/validation/index.md)

## Demonstration

Replay localization, retain `.wout` and declared derived artifacts, then compare Wannier bands with independent identified DFT evidence over one accepted window and validation set.

## Gate

Process completion, localization convergence, spread behavior, and band-interpolation validation remain separate observations. Metrics support only their declared scientific claim.
