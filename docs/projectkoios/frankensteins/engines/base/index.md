# `projectkoios.frankensteins.engines.base`

**Source:** `src/projectkoios/frankensteins/engines/base.py`

`BaseEngine` owns the common immutable identity and validation extracted from
the PyFlamestk and PyPosPack example-engine bindings. It is metadata only and
does not expose `run` or `evaluate` behavior.

## Diff analysis

Both source families repeat four invariant fields: maintained engine name,
normalized example root, exact example Git tree, and root-level Python
entrypoints. Their validation rules were identical, except PyFlamestk had not
previously rejected duplicate entrypoints.

The source-specific differences remain outside the base:

- PyFlamestk owns reconstruction status, blocker limitations, and content-tree
  aliases.
- PyPosPack owns its observed execution surface (`pyposmat`, `lammps`, or
  `vasp`).
- Each source family verifies its own literal example-tree table.
- Reconstruction result types and source-reading strategies remain distinct.

This is deliberately the smallest common contract. Calculator execution and the
future optimizer-neutral evaluator are not inferred from static source-binding
metadata.
