# `MathematicalModelSourceSpan`

**Implemented in:** `projectkoios.frankensteins.mathematics.models`

Binds a mathematical definition or implementation to exact verified file
evidence and an inclusive line range.

## Fields

- `evidence: SourceFileEvidence`
- `first_line: int`
- `last_line: int`

The span must satisfy `1 <= first_line <= last_line <= 1_000_000`.
`to_dict()` nests the evidence identity and both line numbers. A span identifies
source evidence; it does not execute or parse that source by itself.
