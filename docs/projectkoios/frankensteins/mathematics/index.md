# `projectkoios.frankensteins.mathematics`

**Source:** `src/projectkoios/frankensteins/mathematics/`

This package defines immutable contracts for mathematical models extracted from
verified upstream source evidence.

## Package facade

The package re-exports all public contracts implemented in
[`models`](models/index.md):

- `MathematicalModelKind`
- `MathematicalModelSourceSpan`
- `MathematicalModelInput`
- `MathematicalModelDefinition`
- `ExternalMathematicalModelDeclaration`
- `MathematicalModelCatalog`

Only enumerated, closed arithmetic is locally evaluable. Calculator-backed
models remain explicit, evaluation-disabled declarations.
