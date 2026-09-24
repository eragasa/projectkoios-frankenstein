# `projectkoios.frankensteins.engines`

**Source:** `src/projectkoios/frankensteins/engines/`

This package owns source-qualified workflow reconstructions. Each engine is
bound to an exact component revision and one explicit historical example.

## Implemented engine

- [`pyflamestk_lmps_mgo_serial_uniform`](pyflamestk_lmps_mgo_serial_uniform/index.md)
  reconstructs the retained PyFlamestk MgO uniform-sampling example as an
  execution-disabled recipe.

The package-level `__init__.py` exports no shared engine API. Generic contracts
belong to `frankensteins.core`; calculator behavior belongs to
`frankensteins.integrations`.
