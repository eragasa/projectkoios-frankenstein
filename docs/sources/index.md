# External source references

Project Koios Frankenstein refers to externally hosted source repositories and
vendors bounded selections of historical code from their upstream `examples/`
trees. It does not archive, discover, clone, import, execute, or distribute
complete upstream repositories. The machine-readable pins live under the
repository's top-level `sources/` directory.

## Current pins

| Component | Repository | Branch containing the pin | Commit | Git tree | Role |
|---|---|---|---|---|---|
| PyFlamestk | [`eragasa/pyflamestk`](https://github.com/eragasa/pyflamestk) | `master` | `5b8368cc88d91bc56f9cc1c8a7fa8d9ea3d6b359` | `02e20f61a9b554ed0dcbda15bb24adc21e942007` | Exact example-tree catalog and narrow MgO reconstruction |
| PyPosPack | [`eragasa/pypospack`](https://github.com/eragasa/pypospack) | `master`, `release/v0.1.0`, tag `v0.1.0` | `be453fa7191e55a0426f66e8b5b5b0b103c8b29d` | `7ac9c9f255aa7731f39ce35a0e561fc113082a6f` | LAMMPS structure provenance, bounded optimizer and potential cross-checks, and the MgO QOI runtime |
| pymatmc2 | [`eragasa/pymatmc2`](https://github.com/eragasa/pymatmc2) | `master` | `9d31d7fd4f8902f17864fbf391059101a3f5afda` | `7773f886eaecfe919abf68d9e4f990fb398a82be` | Reference-only; no Frankenstein engine yet |

A branch name is context, not immutable provenance. Commits, Git trees, selected
file hashes, byte sizes, and license hashes establish the maintained identity.
For PyFlamestk, the source declaration also points to a literal table of 17 exact
example subtree identities. Strict source revalidation checks every subtree.
For PyPosPack, strict revalidation checks 21 directly selected files: the
original LAMMPS structure source, bounded runner, Buckingham and Tersoff
cross-checks, `qoi.py`, and all 15 files in the historical `qois/` package.

## Vendored example code

The top-level `examples/` directory contains unmodified Python, shell, and
scheduler code selected from each exact pinned upstream `examples/` tree:

- `examples/pyflamestk/`: 172 code files;
- `examples/pypospack/`: 492 code files; and
- `examples/pymatmc2/`: no code files, because the pinned source tree has no
  `examples/` directory.

Each component directory includes the applicable upstream `LICENSE`, a
human-readable `VENDORING.md`, and a machine-readable `PROVENANCE.json`. The
manifest records the repository, revision, tree, selection rule, original path,
Git mode, Git blob identity, SHA-256 digest, and byte size for every vendored
file. Simulation inputs, configuration, data, plots, logs, generated outputs,
and source-package modules are outside this broad code selection. The bounded
`examples/pypospack/MgO/buck/` representation additionally selects its exact
historical configuration, five structures, iterative-sampler implementation,
and QOI runtime under a dedicated provenance manifest. Its maintained adapter
validates the immutable scientific input separately from machine-specific
execution settings. A manifest-driven vendoring recipe reproduces the selection
from committed Git objects.
The vendored code is historical evidence, is excluded from the wheel, and is
not a numerical-verification or scientific-validation claim.

## PyFlamestk example-source coverage

The bound source contains 17 paths with the configuration, LAMMPS-template, and
structure layout of an example engine. Their exact Git tree identities are
recorded in `sources/pyflamestk.toml` under `selection.example_trees` and checked
by strict source revalidation. Duplicate content remains path-qualified provenance rather than
being collapsed.

The only currently maintained runtime reconstruction is the narrow
`lmps_MgO_serial_uniform` workflow. The
[PyFlamestk MgO implementation plan](../plans/pyflamestk-mgo-frankenstein-cpn.md)
defines how the remaining source examples become maintained worked scenarios.
The historical surface example remains deferred because its QOI vocabulary is
not recognized by the same bound PyFlamestk QOI module.

## Release status

- PyFlamestk publishes alpha release `v0.1.0`; its Frankenstein pin remains at
  the earlier source object pending separate contract revalidation.
- PyPosPack publishes alpha release `v0.1.0` and exposes
  `release/v0.1.0`. The tag, release branch, and `master` resolve to the exact
  commit pinned here.
- pymatmc2 exposes `master` and `develop`; tag `v0.1` identifies its current
  source baseline.

Frankenstein does not invent release status for an upstream repository. A moving
branch is never used as a substitute for an exact source pin.

## Planned pin updates

The PyPosPack pin was advanced to its v0.1.0 release only after complete
selected-contract revalidation. The PyFlamestk pin still requires a future
owner-repository update. Advancing either pin again must be a deliberate
revalidation, not an automatic branch-head update. A pin change must update and
verify, as applicable:

1. repository URL, exact commit, and Git tree;
2. selected source paths, SHA-256 digests, and byte sizes;
3. license path and digest;
4. definition and implementation source spans;
5. reconstruction and adversarial tests;
6. CI checkout revisions; and
7. this documentation and the machine-readable source declaration.

pymatmc2 remains reference-only until a bounded behavior is selected, extracted,
and tested. Its presence in `sources/pymatmc2.toml` does not imply an engine,
runtime compatibility, numerical verification, or scientific validation.

## Local checkout convention

Operator-managed checkouts may live at:

```text
~/repos/pyflamestk
~/repos/pypospack
~/repos/pymatmc2
```

The paths are not provenance and never appear in serialized artifacts. Tests use
explicit environment variables for checkouts that support maintained behavior:

```bash
export PYFLAMESTK_CHECKOUT="$HOME/repos/pyflamestk"
export PYPOSPACK_CHECKOUT="$HOME/repos/pypospack"
```

No pymatmc2 checkout variable is defined until a concrete engine or integration
owns a bounded verification contract.
