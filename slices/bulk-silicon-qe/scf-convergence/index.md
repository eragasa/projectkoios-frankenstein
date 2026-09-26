# Slice: bulk-silicon SCF convergence

**Status:** Complete — replayed policy outcome

## Outcome

Produce provenance-bound accepted mesh and cutoff settings, or one bounded non-acceptance outcome, for the reviewed initial silicon structure.

## Consumed tasks

- [QE retained SCF convergence evidence](../../../tasks/qe/retained-scf-convergence-evidence/index.md)
- [QE SCF convergence workflow](../../../tasks/workflow/qe/scf-convergence/index.md)
  - [K-point subtask](../../../tasks/workflow/qe/scf-convergence/subtasks/k-points/index.md)
  - [Cutoff subtask](../../../tasks/workflow/qe/scf-convergence/subtasks/wavefunction-cutoff/index.md)
  - [Joint-confirmation subtask](../../../tasks/workflow/qe/scf-convergence/subtasks/joint-confirmation/index.md)

## Demonstration

Replay retained QE observations through the maintained convergence controller and produce an assessment whose evidence declarations retain native artifact, executable, pseudopotential, structure, and policy identities.

## Recorded outcome

The complete retained grid contains 30 initial points and the six adaptive points requested by the maintained controller. Replay terminates in policy acceptance at mesh density `14` and wavefunction cutoff `40 Ry`.

Final neighboring-point deltas are:

- k-point edge: `0.2876923810788412` and `0.05986504976362994 meV/atom`;
- cutoff edge: `0.5384453053522975` and `0.31735279210920453 meV/atom`.

Evidence and replay instructions are recorded in the [bulk-silicon QE convergence example](../../../examples/projectkoios/Si/bulk/qe_wannier90/scf_convergence/README.md).

## Gate

Passed. Synthetic control data is not presented as scientific evidence; finite-grid acceptance is qualified; all axis and joint extensions are bounded. This outcome establishes total-energy convergence under the declared policy only.
