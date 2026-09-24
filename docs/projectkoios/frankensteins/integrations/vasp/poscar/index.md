# `projectkoios.frankensteins.integrations.vasp.poscar`

**Source:** `.../integrations/vasp/poscar.py`

## Public API

- [`VaspStructureObservation`](VaspStructureObservation/index.md)
- `inspect_poscar(name, evidence, text)` performs bounded, read-only POSCAR
  inspection.

## Inspection behavior

The function limits UTF-8 input to 10 MB and requires a comment, finite nonzero
scale, three finite lattice vectors, positive element counts, a supported
coordinate mode, and enough finite three-value coordinate rows. It accepts both
symbol-bearing VASP 5 style and count-only VASP 4 style, recognizes optional
selective-dynamics lines, and normalizes `Direct` prefixes to `direct` and
`Cartesian` or source-format `K` prefixes to `cartesian`.

Only the first three values of each coordinate row are inspected; optional
selective flags are not retained. Extra trailing rows are not interpreted. The
internal `_three_finite_floats` helper performs numeric validation.
