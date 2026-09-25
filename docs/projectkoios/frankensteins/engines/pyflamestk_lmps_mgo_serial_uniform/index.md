# `projectkoios.frankensteins.engines.pyflamestk_lmps_mgo_serial_uniform`

**Source:** `src/projectkoios/frankensteins/engines/pyflamestk_lmps_mgo_serial_uniform/`

This package incubates maintained components reconstructed from the exact
PyFlamestk MgO serial-uniform example. Implementations are imported from their
defining modules rather than broadly re-exported by a package facade.

- [`constants`](constants/index.md) owns external source identity.
- [`charge_distribution`](charge_distribution/index.md) constructs the exact
  historical magnesium-charge distribution.
- [`reconstruction`](reconstruction/index.md) documents checkout-backed
  reconstruction evidence.
- [`mathematical_models`](mathematical_models/index.md) documents reconstructed
  closed arithmetic.

The package does not import or execute upstream PyFlamestk modules or scripts.
A runnable optimization feedback-loop engine remains the next composition
boundary.
