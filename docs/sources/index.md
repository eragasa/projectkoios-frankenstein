# External source references

Project Koios Frankenstein refers to externally hosted source repositories. It
does not vendor, archive, discover, clone, import, or execute them. The
machine-readable pins live under the repository's top-level `sources/`
directory.

## Current pins

| Component | Repository | Branch containing the pin | Commit | Git tree | Role |
|---|---|---|---|---|---|
| PyFlamestk | [`eragasa/pyflamestk`](https://github.com/eragasa/pyflamestk) | `master` | `5b8368cc88d91bc56f9cc1c8a7fa8d9ea3d6b359` | `02e20f61a9b554ed0dcbda15bb24adc21e942007` | Current MgO workflow reconstruction |
| PyPosPack | [`eragasa/pypospack`](https://github.com/eragasa/pypospack) | `master` | `21cdecaf3b05c87acc532d992be2c04d85bfbc22` | `a5a4cee972e487512275c34f308251e6cc38c2fa` | Current LAMMPS reconstruction |
| pymatmc2 | [`eragasa/pymatmc2`](https://github.com/eragasa/pymatmc2) | `master` | `9d31d7fd4f8902f17864fbf391059101a3f5afda` | `7773f886eaecfe919abf68d9e4f990fb398a82be` | Reference-only; no Frankenstein engine yet |

A branch name is context, not immutable provenance. Commits, Git trees, selected
file hashes, byte sizes, and license hashes establish the maintained identity.

## Release status

- PyFlamestk exposes `master` and currently has no release branch or tag.
- PyPosPack exposes `master` and currently has no release branch or tag.
- pymatmc2 exposes `master` and `develop`; tag `v0.1` identifies its current
  source baseline.

Frankenstein does not invent release status for an upstream repository. A moving
branch is never used as a substitute for an exact source pin.

## Planned pin updates

The PyFlamestk and PyPosPack pins require future owner-repository updates. The
corresponding code contains explicit `TODO` comments. Advancing either pin must
be a deliberate revalidation, not an automatic branch-head update. A pin change
must update and verify, as applicable:

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
