# `projectkoios.frankensteins.mathematics.models`

**Source:** `src/projectkoios/frankensteins/mathematics/models.py`

This module owns version `0.1.0` immutable mathematical-model contracts and
closed arithmetic evaluation.

## Classes

- [`MathematicalModelKind`](MathematicalModelKind/index.md)
- [`MathematicalModelSourceSpan`](MathematicalModelSourceSpan/index.md)
- [`MathematicalModelInput`](MathematicalModelInput/index.md)
- [`MathematicalModelDefinition`](MathematicalModelDefinition/index.md)
- [`ExternalMathematicalModelDeclaration`](ExternalMathematicalModelDeclaration/index.md)
- [`MathematicalModelCatalog`](MathematicalModelCatalog/index.md)

## Module constraints

Identifiers and source-model types use bounded explicit grammars; source
revisions are exact Git SHA-1 values. Models and catalogs derive stable IDs
from complete serialized identity material. All scalar inputs and results must
be finite. The module never evaluates a string expression or calls an external
backend.
