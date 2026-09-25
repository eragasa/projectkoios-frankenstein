# `pyflamestk_examples.reconstruction`

**Source:** `src/projectkoios/frankensteins/engines/pyflamestk_examples/reconstruction.py`

`reconstruct_example_engine(checkout_root, engine_name)` reconstructs one
supported binding from an explicit checkout of the exact PyFlamestk source. It:

1. rejects blocked or unknown engine names;
2. verifies the license identity;
3. reproduces and verifies the complete example Git tree identity without
   invoking Git or executing source code;
4. reads bounded regular-file evidence without following symbolic links;
5. parses configuration settings and protected LAMMPS command intents,
   normalizing a source-pinned absolute LAMMPS executable to the maintained
   `LAMMPS_BIN` boundary;
6. inspects declared VASP or LAMMPS data structures, including the historical
   `lmmps` file-type spelling when exact data syntax confirms the intent;
7. reconstructs the shared QOI catalog and a closed Buckingham or Tersoff
   external-model declaration; and
8. returns an execution-disabled `FrankensteinRecipe` with no local path.

The Tersoff variant retains explicit warnings for the defective historical
PyFlamestk implementation and the source example's Si-potential/MgO-structure
mismatch. Its interpretation is referenced to the official
[LAMMPS Tersoff documentation](https://docs.lammps.org/pair_tersoff.html), the
literature cited there, and an exactly pinned PyPosPack implementation
cross-check. Full citations are maintained in the
[mathematical-model documentation](../../pyflamestk_lmps_mgo_serial_uniform/mathematical_models/index.md).

Historical Python entrypoints remain hashed source evidence. They are never
imported or executed.
