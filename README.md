# projectkoios-frankenstein

Provenance-bound, execution-disabled reconstructions of externally hosted
scientific workflows.

This repository contains maintained reconstruction code plus bounded selections
of historical upstream example code under [`examples/`](examples/). It does not
copy, archive, or distribute complete upstream repositories. Exact external
references are declared under [`sources/`](sources/):

- [PyFlamestk](https://github.com/eragasa/pyflamestk) at
  `5b8368cc88d91bc56f9cc1c8a7fa8d9ea3d6b359`
- [PyPosPack](https://github.com/eragasa/pypospack) release `v0.1.0` at
  `be453fa7191e55a0426f66e8b5b5b0b103c8b29d`
- [pymatmc2](https://github.com/eragasa/pymatmc2) at
  `9d31d7fd4f8902f17864fbf391059101a3f5afda` as a reference-only pin

PyFlamestk and PyPosPack currently support maintained reconstructions. The
PyFlamestk source declaration preserves the exact Git tree identities of all 17
engine-shaped example paths; the maintained runtime reconstruction remains the
narrow MgO serial-uniform workflow until the planned adapters are implemented.
pymatmc2 is pinned for provenance only and has no Frankenstein engine yet. See
the [external-source reference policy](docs/sources/index.md) for release status
and pin-update requirements.

The vendored example selection contains Python, shell, and scheduler code from
the exact pinned upstream `examples/` trees: 172 PyFlamestk files and 492
PyPosPack files. The pinned pymatmc2 revision has no `examples/` tree. Each
repository directory preserves the upstream license and records every copied
file's original path, Git blob identity, SHA-256 digest, byte size, and mode in
`PROVENANCE.json`. The broad example-code selection excludes simulation inputs,
data, plots, logs, generated outputs, and source-package modules. The bounded
`examples/pypospack/MgO/buck/` representation additionally selects its exact
configuration, five structures, iterative-sampler implementation, and historical
QOI runtime under a separate provenance manifest.

Callers provide explicit local checkouts when verifying or reconstructing those
sources. Package code never discovers, downloads, imports, or executes upstream
code, and the vendored example code is not included in the package.

## Safety boundary

Reconstruction may parse verified source text and calculate closed finite
arithmetic expressions implemented in this repository. It never authorizes
LAMMPS, VASP, scheduler, shell, or arbitrary Python execution. A reconstructed
artifact makes no numerical-verification or scientific-validation claim.

## Desired architecture

The [architecture documents](docs/architecture/index.md) model potential fitting
as a `MultiObjectiveOptimizer` operating on a `PotentialOptimization` problem.
They separate material-property observations, objective transforms, calculator
execution, reusable inheritable CPN fragments, and historical conformance
adapters. Generic CPN ownership targets `projectkoios-cpn`; orchestration targets
`projectkoios-workflow`. The PyFlamestk `lmps_MgO_*` reconstructions are used as
worked scenarios through the current `FrankensteinRecipe` boundary rather than
as legacy runtime entrypoints. Target design is explicitly distinguished from
implemented, numerically verified, and scientifically validated behavior.

## Development

See [`docs/index.md`](docs/index.md) and
[`docs/development/index.md`](docs/development/index.md). CI checks out the
upstream repositories at exact commits into an ignored workspace directory,
runs conformance tests, builds the wheel, and verifies its package boundary.
