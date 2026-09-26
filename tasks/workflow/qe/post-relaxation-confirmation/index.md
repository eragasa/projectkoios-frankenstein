# QE post-relaxation confirmation workflow

**Task:** `workflow-qe-post-relaxation-confirmation`

**Status:** Proposed

## Objective

Verify selected mesh and cutoff settings on the retained relaxed structure.

## Subtasks

- [Policy](subtasks/policy/index.md)
- [Controller](subtasks/controller/index.md)

## Dependencies

- Structural-relaxation terminal success.
- Maintained SCF convergence child workflows.
- Accepted neighboring-coordinate and finite re-entry policy.

## Outputs

Confirmed settings, bounded scientific extension, exhausted outcome, or failure.

## Acceptance

Evidence is tied to the relaxed structure. Re-entry cycles, grid extensions, calculator jobs, and retries have separate finite bounds.
