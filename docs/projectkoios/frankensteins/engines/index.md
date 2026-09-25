# `projectkoios.frankensteins.engines`

**Source:** `src/projectkoios/frankensteins/engines/`

This package owns source-qualified workflow reconstructions. Each engine is
bound to an exact component revision and one explicit historical example.

## Implemented engines

- [`BaseEngine`](base/index.md) is the shared immutable identity contract
  extracted from the PyFlamestk and PyPosPack binding diff.
- [`pyflamestk_examples`](pyflamestk_examples/index.md) catalogs every
  engine-shaped example in the bound PyFlamestk source and reconstructs all
  variants that satisfy the maintained static contract.
- [`pyflamestk_lmps_mgo_serial_uniform`](pyflamestk_lmps_mgo_serial_uniform/index.md)
  preserves the original narrow MgO uniform-sampling API as an
  execution-disabled recipe.
- [`pypospack_examples`](pypospack_examples/index.md) catalogs 31 exact
  PyPosPack example trees with 37 engine entrypoints and reconstructs their
  evidence and execution boundaries without importing or running PyPosPack.

The package-level `__init__.py` exports only `BaseEngine`. Generic recipe and
evidence contracts remain in `frankensteins.core`; calculator behavior remains
in `frankensteins.integrations`.
