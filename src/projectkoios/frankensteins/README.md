# Frankenstein engines

This directory owns maintained engines reconstructed from explicitly referenced
external workflow examples.

Each engine is source-qualified. Calculator-specific behavior remains under
explicit integration namespaces such as `integrations/lammps/` and
`integrations/vasp/`.

An engine accepts an explicit checkout and verifies only declared source paths,
hashes, and sizes. It never fetches, imports, or executes upstream code. No
calculator or scheduler execution is authorized by an engine's presence.

## Initial maintained slice

`engines/pyflamestk_lmps_mgo_serial_uniform/` reconstructs the externally hosted
PyFlamestk MgO uniform-sampling example as a content-addressed,
execution-disabled recipe. The `mathematics` package owns closed finite scalar
models reconstructed from exact source spans while preserving source-declared
unused inputs and rejecting arbitrary expression evaluation.

The canonical `integrations/lammps/` package also contains an effect-free LAMMPS
data renderer bound to an exact external PyPosPack source file. It accepts only
explicit atom data and diagonal cells, returns text in memory, and never writes
files or executes LAMMPS. There is no parallel singular `integration/`
namespace.
