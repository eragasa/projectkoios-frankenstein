# `pyflamestk-lmps-mgo-serial-uniform`

This provisional engine reconstructs the externally hosted PyFlamestk example
[`examples/lmps_MgO_serial_uniform`](https://github.com/eragasa/pyflamestk/tree/5b8368cc88d91bc56f9cc1c8a7fa8d9ea3d6b359/examples/lmps_MgO_serial_uniform)
at exact Git revision `5b8368cc88d91bc56f9cc1c8a7fa8d9ea3d6b359`.

Callers provide an explicit local checkout. The package never clones or fetches
source. Reconstruction:

- verifies every selected file against its bound SHA-256 digest and byte size;
- verifies the upstream license identity;
- parses sampling, potential, structure, simulation, quantity-of-interest, and
  target settings without importing or executing upstream code;
- reconstructs finite scalar models with exact definition and implementation
  spans;
- routes LAMMPS and POSCAR inspection through protected integration boundaries;
- removes machine-specific executable paths; and
- emits a content-addressed, execution-disabled JSON recipe.

The arithmetic rewrite preserves a source-declared awkward detail: bulk and
shear models require `c44`, but their expressions do not use it. The input
remains in the model contract with `participates_in_expression=false`.

The example declares Buckingham `buck/coul/long` interactions, but their full
semantics remain delegated to LAMMPS. This package does not execute LAMMPS or
VASP, evaluate arbitrary source expressions, select pseudopotentials, create
calculator outputs, claim numerical verification, or claim scientific
validation.
