# Implement Wannier90 output models

**Task:** `wannier-output`

**Status:** Proposed

## Objective

Represent supported Wannier90 native output families and extract bounded observations without discarding source bytes.

## Subtasks

- [`.wout` parser](subtasks/wout-parser/index.md)
- [Hamiltonian artifact declaration](subtasks/hamiltonian-declaration/index.md)

## Outputs

Native completion, convergence, iteration, spread, center, diagnostic, and declared derived-artifact observations.

## Acceptance

Each parser has an accepted version/build contract; unsupported formats remain typed explicit stubs.
