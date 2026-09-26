# Implement Wannier90 execution boundary

**Task:** `wannier-execution`

**Status:** Proposed

## Objective

Provide bounded no-shell execution for accepted Wannier90 modes while preserving complete evidence.

## Subtasks

- [Preflight](subtasks/preflight/index.md)
- [Executor](subtasks/executor/index.md)

## Outputs

Execution request and record with exact executable, arguments, inputs, streams, timeout, status, and workspace evidence.

## Acceptance

No execution occurs without exact resource identity and explicit external authorization.
