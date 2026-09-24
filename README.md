# projectkoios-frankenstein

Provenance-bound, execution-disabled reconstructions of externally hosted
scientific workflows.

This repository contains maintained reconstruction code only. It does not copy,
vendor, archive, or distribute the upstream source repositories. Exact external
references are declared under [`sources/`](sources/):

- [PyFlamestk](https://github.com/eragasa/pyflamestk) at
  `5b8368cc88d91bc56f9cc1c8a7fa8d9ea3d6b359`
- [PyPosPack](https://github.com/eragasa/pypospack) release `v0.1.0` at
  `be453fa7191e55a0426f66e8b5b5b0b103c8b29d`
- [pymatmc2](https://github.com/eragasa/pymatmc2) at
  `9d31d7fd4f8902f17864fbf391059101a3f5afda` as a reference-only pin

PyFlamestk and PyPosPack currently support maintained reconstructions. pymatmc2
is pinned for provenance only and has no Frankenstein engine yet. See the
[external-source reference policy](docs/sources/index.md) for release status and
pin-update requirements.

Callers provide explicit local checkouts when verifying or reconstructing those
sources. Package code never discovers, downloads, imports, or executes upstream
code.

## Safety boundary

Reconstruction may parse verified source text and calculate closed finite
arithmetic expressions implemented in this repository. It never authorizes
LAMMPS, VASP, scheduler, shell, or arbitrary Python execution. A reconstructed
artifact makes no numerical-verification or scientific-validation claim.

## Development

See [`docs/index.md`](docs/index.md) and
[`docs/development/index.md`](docs/development/index.md). CI checks out the
upstream repositories at exact commits into an ignored workspace directory,
runs conformance tests, builds the wheel, and verifies its package boundary.
