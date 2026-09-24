# `pyflamestk_lmps_mgo_serial_uniform.mathematical_models`

**Source:** `.../pyflamestk_lmps_mgo_serial_uniform/mathematical_models.py`

`reconstruct_mathematical_models(checkout_root)` reads five explicitly selected
files from an operator-provided PyFlamestk checkout. `_verified_text` enforces
the path, byte bound, exact digest, exact size, and strict UTF-8 decoding against
`SOURCE_FILES` before parsing.

The module reconstructs:

- one dependent-charge negation;
- identity quantities of interest;
- cubic bulk and tetragonal shear moduli;
- defect-formation energies;
- surface energy; and
- an execution-disabled external Buckingham declaration.

Parsing is closed and enumerated. `_external_potential_models`,
`_dependent_parameter_models`, `_qoi_models`, `_qoi_model_contract`, and
`_verify_implementation_spans` do not evaluate source expressions. Exact source
spans remain attached to every definition and implementation.
