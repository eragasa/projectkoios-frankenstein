# `projectkoios.frankensteins.__main__`

**Source:** `src/projectkoios/frankensteins/__main__.py`

This module is the CLI adapter for the `koios-frankenstein` console script.

## Functions

### `parser() -> argparse.ArgumentParser`

Builds the command parser. The sole command is
`inspect-pyflamestk-mgo`. It requires `--pyflamestk-checkout` and accepts an
optional `--output` path.

### `main(arguments: list[str] | None = None) -> int`

Reconstructs the execution-disabled MgO recipe from an explicit PyFlamestk
checkout. Without `--output`, it writes JSON to standard output. With `--output`, it
creates a new file and refuses to overwrite any existing path or symlink.

The adapter resolves the checkout root but does not fetch source or execute
LAMMPS or VASP.
Its output behavior is the only intentional filesystem effect in the packaged
reconstruction code.
