# Slice: QE-to-Wannier90 interface

**Status:** Proposed

## Outcome

Produce a retained `.nnkp` declaration and correlated QE interface artifacts from one accepted NSCF state.

## Consumed tasks

- [Wannier90 input](../../../tasks/wannier/input/index.md)
- [Wannier90 preprocessing integration](../../../tasks/wannier/preprocessing/index.md)
- [`pw2wannier90.x` integration](../../../tasks/qe/pw2wannier90/index.md)
- [Wannier90 preprocessing workflow](../../../tasks/workflow/wannier/preprocessing/index.md)

## Demonstration

Replay `.win` rendering, Wannier90 preprocessing, and QE conversion. Join NSCF and `.nnkp` identities before accepting `.amn`, `.mmn`, `.eig`, or other declared converter artifacts.

## Gate

K-point order, structure, prefix, band count, and Wannier-function count agree across every input; required artifacts fail closed when missing or mismatched.
