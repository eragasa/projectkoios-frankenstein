# `projectkoios.frankensteins.io.vasp.poscar`

The format authority is the official VASP [`POSCAR`](https://vasp.at/wiki/POSCAR) documentation retained as `POSCAR_DOCUMENTATION_URL`.

`UnitCellModel` binds the shared unit cell to the POSCAR boundary. `PoscarModel` adds the POSCAR comment and delegates its public `write` action to `PoscarWriter`. `PoscarWriter` provides deterministic `render` and atomic `write` actions. It computes the physical cell matrix `H = lattice_parameter × A`, converts `H` to Å, emits a scale of `1.0`, groups sites by first-occurring element symbol, and emits fractional coordinates under `Direct`.

The writer performs representation and filesystem serialization only. It does not standardize cells, wrap fractional coordinates, select structures, or execute VASP.
