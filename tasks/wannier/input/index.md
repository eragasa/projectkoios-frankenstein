# Implement Wannier90 input model

**Task:** `wannier-input`

**Status:** Proposed

## Objective

Represent and render the accepted Wannier90 input declaration without selecting scientific values implicitly.

## Subtasks

- [`.win` declaration](subtasks/win-declaration/index.md)
- [Deterministic writer](subtasks/writer/index.md)

## Outputs

Immutable native declaration and deterministic `.win` text.

## Acceptance

Projections, functions, bands, k points, windows, and requested outputs are explicit; unsupported syntax fails before execution where bounded validation is possible.
