# `projectkoios.frankensteins.engines.pyflamestk_lmps_mgo_serial_uniform`

**Source:** `src/projectkoios/frankensteins/engines/pyflamestk_lmps_mgo_serial_uniform/`

This package reconstructs one exact externally hosted PyFlamestk MgO example.
Its facade exports `ENGINE_NAME`, `EXAMPLE_ROOT`, `SOURCE_REPOSITORY_URL`,
`SOURCE_REVISION`, `SOURCE_TREE`, `reconstruct_checkout`, and
`reconstruct_mathematical_models`.

- [`constants`](constants/index.md) owns external source identity.
- [`reconstruction`](reconstruction/index.md) verifies an explicit checkout and
  composes the recipe.
- [`mathematical_models`](mathematical_models/index.md) owns closed arithmetic
  reconstruction.

The package never fetches, imports, or executes the referenced repository.
