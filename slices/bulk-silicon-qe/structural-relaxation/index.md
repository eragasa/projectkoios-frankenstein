# Slice: bulk-silicon structural relaxation

**Status:** Proposed

## Outcome

Replay one accepted QE relaxation declaration into one immutable relaxed structure or one explicit terminal failure.

## Consumed tasks

- [QE structural-relaxation integration](../../../tasks/qe/structural-relaxation/index.md)
- [QE structural-relaxation workflow](../../../tasks/workflow/qe/structural-relaxation/index.md)

## Demonstration

Render reviewed `pw.x` input, analyze retained relaxation output, preserve force/stress/cell evidence, and construct a new structure linked to the immutable initial structure.

## Gate

The calculation role and numerical policy are accepted; final geometry extraction fails closed; replay passes without calculator execution.
