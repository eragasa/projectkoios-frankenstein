# `projectkoios.frankensteins.integrations.lammps`

**Source:** `src/projectkoios/frankensteins/integrations/lammps/`

Effect-free LAMMPS reconstruction boundary.

## Modules

- [`models`](models/index.md) defines protected template and command observations.
- [`inspection`](inspection/index.md) reconstructs those observations from
  verified runner-script text.
- [`provenance`](provenance/index.md) verifies selected files in an explicit
  checkout of the exact external PyPosPack revision.
- [`structure`](structure/index.md) deterministically renders bounded LAMMPS
  data-file text in memory.

The package facade re-exports the public classes, source identity constants,
`inspect_lammps_templates`, `verify_pypospack_lammps_checkout`, and
`render_lammps_data`. None of these APIs invokes LAMMPS or writes a data file.
