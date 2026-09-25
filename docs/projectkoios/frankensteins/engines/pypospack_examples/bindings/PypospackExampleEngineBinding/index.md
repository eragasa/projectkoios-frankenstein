# `PypospackExampleEngineBinding`

Immutable source binding for one bounded PyPosPack example engine. It inherits
the common identity fields and validation from `BaseEngine`.

## Fields

- `engine_name`: maintained reconstruction identifier.
- `example_root`: normalized path below upstream `examples/`.
- `example_tree`: exact Git tree SHA-1 at the pinned revision.
- `entrypoints`: one or more root-level historical Python files.
- `execution_surface`: `pyposmat`, `lammps`, or `vasp`.

Construction validates every field against the literal source-tree table.
