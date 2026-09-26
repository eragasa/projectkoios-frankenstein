# QE structural-relaxation workflow

**Task:** `workflow-qe-structural-relaxation`

**Status:** Proposed

## Objective

Drive one accepted relaxation request through registration, execution or replay, native analysis, and immutable relaxed-structure production.

## Subtasks

- [Contracts](subtasks/contracts/index.md)
- [Workflow definition](subtasks/definition/index.md)
- [Replay](subtasks/replay/index.md)

## Dependencies

- [`qe-structural-relaxation-integration`](../../../qe/structural-relaxation/index.md)
- Accepted SCF settings and relaxation declaration.

## Outputs

One relaxed-structure result or one explicit terminal failure.

## Acceptance

The initial structure is immutable; successful output carries exact final geometry and evidence identity; infrastructure failure and numerical nonconvergence remain distinct.
