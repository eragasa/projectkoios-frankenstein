# `pyflamestk_lmps_mgo_serial_uniform.reconstruction`

**Source:** `.../pyflamestk_lmps_mgo_serial_uniform/reconstruction.py`

This module performs deterministic static reconstruction from an explicit local
checkout of the exact externally referenced PyFlamestk revision.

## Public API

`reconstruct_checkout(checkout_root)`:

1. verifies the bound license digest;
2. opens only explicitly selected paths from `SOURCE_FILES`;
3. verifies every selected file's SHA-256 digest and byte size;
4. decodes source as strict UTF-8;
5. reconstructs settings, protected LAMMPS command intent, VASP observations,
   and mathematical models; and
6. returns an execution-disabled `FrankensteinRecipe` containing only portable
   source identities, never the local checkout path.

Internal `_settings`, `_literal_assignment`, and `_warnings` helpers provide
closed parsing and explicit observations.
No helper imports or executes upstream code.
