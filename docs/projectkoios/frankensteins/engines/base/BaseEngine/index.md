# `BaseEngine`

`BaseEngine` is the common frozen identity contract for one source-qualified
historical example engine.

## Fields

- `engine_name`: bounded maintained identifier.
- `example_root`: normalized path below the upstream `examples/` directory.
- `example_tree`: exact Git tree SHA-1.
- `entrypoints`: unique root-level historical Python entrypoints.

The class validates identity only. It does not reconstruct source evidence,
launch a calculator, invoke an optimizer or scheduler, or provide `run` or
`evaluate` methods. Source-specific subclasses retain source-tree-table,
disposition, alias, and execution-surface rules.
