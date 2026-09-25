# `pypospack_examples.bindings`

**Source:** `src/projectkoios/frankensteins/engines/pypospack_examples/bindings.py`

`PypospackExampleEngineBinding` binds one maintained engine name to an exact
PyPosPack example root, Git tree, root-level Python entrypoints, and execution
surface.

`SOURCE_EXAMPLE_TREES` contains the 31 source-tree identities checked by the
source revalidation tool. `ENGINE_BINDINGS` is the immutable catalog.
`engine_binding(engine_name)` returns an exact binding and rejects unknown
names.
