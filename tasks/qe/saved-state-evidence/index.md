# Define QE saved-state evidence

**Task:** `qe-saved-state-evidence`

**Status:** Proposed

## Objective

Represent the QE native state passed from production SCF to NSCF and from NSCF to `pw2wannier90.x` without treating a mutable directory as an unqualified artifact.

## Subtasks

- [Manifest](subtasks/manifest/index.md)
- [Bounded inspection](subtasks/bounded-inspection/index.md)

## Inputs

- Identified QE output directory after a completed calculation.
- Accepted file-family and size policy.

## Outputs

- Immutable manifest of required relative paths, roles, hashes, byte sizes, producer task, QE version, structure, and pseudopotential identities.

## Acceptance

- Paths are relative, normalized, nonsymbolic, and bounded.
- Missing or concurrently changed files fail closed.
- The manifest distinguishes durable evidence from disposable scratch content.

## Non-goals

- Serializing mutable QE runtime objects.
- Packaging entire unreviewed output directories into the wheel.
