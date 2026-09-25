# `projectkoios.frankensteins.engines.pypospack_examples`

**Source:** `src/projectkoios/frankensteins/engines/pypospack_examples/`

This package catalogs and statically reconstructs the bounded engine-shaped
examples in the exact PyPosPack source declaration. PyPosPack remains external,
immutable source evidence; no upstream module, script, calculator, optimizer,
or scheduler is imported or executed.

## Bounded catalog contract

An example enters this first catalog when a committed Python file under
`examples/` visibly selects at least one of these execution surfaces:

- a class from `pypospack.pyposmat.engines`;
- `VaspSimulation`;
- a PyPosPack LAMMPS task; or
- the historical LAMMPS NEB workflow class.

The catalog contains 31 exact example trees and 37 historical entrypoints:
23 PyPosMat roots, 6 VASP roots, and 2 direct LAMMPS roots. This does not treat
plotting scripts, structure generators, or data-analysis utilities as engines.

`bindings.SOURCE_EXAMPLE_TREES` is a literal table of Git tree identities. It is
referenced by `sources/pypospack.toml`, so source revalidation checks each tree
against the declared PyPosPack commit.

## Reconstruction boundary

`reconstruct_example_engine(checkout_root, engine_name)`:

1. verifies the bound license hash and example Git tree identity;
2. records SHA-256 and byte size for every regular file in the example tree;
3. records the historical entrypoints and observed execution surface; and
4. returns an immutable, deterministic reconstruction with execution and
   scientific-validation claims disabled.

The checkout path is never serialized. Historical Python and YAML are retained
as evidence only. In particular, the legacy
`!!python/object/apply:collections.OrderedDict` YAML form is not loaded by this
static reconstruction.
