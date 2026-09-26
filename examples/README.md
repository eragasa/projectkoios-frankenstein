# Examples

## Maintained Project Koios examples

- [`projectkoios/Si/single_scf`](projectkoios/Si/single_scf/README.md) separates silicon single-SCF, convergence, and qualified QE/VASP comparison examples.

## Vendored upstream evidence

The `pyflamestk/`, `pypospack/`, and `pymatmc2/` directories preserve example code from exact upstream revisions pinned in `sources/`. Each repository directory contains its upstream license and a per-file provenance manifest. The broad code selection excludes data, outputs, plots, and source-package modules. The bounded `pypospack/MgO/buck/` representation additionally preserves its exact source configuration, required structures, one explicitly selected sampler implementation, and historical QOI runtime under a dedicated provenance manifest and reproducible vendoring recipe. The `pypospack/Si/vasp/struct_min/` representation preserves a working silicon VASP structural-minimization fixture, a compact reproduced result, and identities for the deliberately external executable, pseudopotential, and native outputs.

- `pyflamestk/`: 172 code files
- `pypospack/`: 492 code files
- `pymatmc2/`: 0 code files
