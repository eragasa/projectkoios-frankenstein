# `pyflamestk_lmps_mgo_serial_uniform.mathematical_models`

**Source:** `.../pyflamestk_lmps_mgo_serial_uniform/mathematical_models.py`

`reconstruct_mathematical_models(checkout_root)` reads five explicitly selected
files from the original operator-provided PyFlamestk example binding.
`reconstruct_mathematical_models_for_example(checkout_root, *,
source_example_root, source_files)` applies the same closed extraction to another
tree-verified example with explicit source identities. `_verified_text` enforces
the path, byte bound, exact digest, exact size, and strict UTF-8 decoding against
the supplied binding before parsing.

The module reconstructs:

- one dependent-charge negation;
- identity quantities of interest;
- cubic bulk and tetragonal shear moduli;
- defect-formation energies;
- surface energy; and
- execution-disabled external Buckingham and Tersoff declarations, selected by
  the exact potential configuration.

The external declaration follows the official LAMMPS
[`pair_style buck/coul/long`](https://docs.lammps.org/pair_buck.html) contract:
the Buckingham term is $A\exp(-r/\rho)-C/r^6$, coefficients are $A$, $\rho$,
and $C$, and every atom-type pair requires an explicit coefficient because the
style does not support mixing. Historical lowercase `a` and `c` configuration
labels are therefore normalized only for completeness checks; their exact
source spellings remain in the declared parameter variables. The source also
selects `kspace_style pppm` for the long-range Coulomb contribution. This
external documentation supports interpretation but does not replace the pinned
PyFlamestk source evidence.

The Tersoff declaration follows the official LAMMPS
[`pair_style tersoff`](https://docs.lammps.org/pair_tersoff.html) contract. It
records ordered element triplets and the exact LAMMPS file order `m`, `gamma`,
`lambda3`, `c`, `d`, `costheta0`, `n`, `beta`, `lambda2`, `B`, `R`, `D`,
`lambda1`, and `A`. It neither evaluates the potential nor writes a parameter
file. The source example is preserved with two explicit warnings: its historical
PyFlamestk Tersoff class contains unresolved defects, and its Si potential is
paired with Mg/O structures. Reconstruction therefore conveys source intent,
not a runnable or scientifically valid simulation.

The pinned PyPosPack file
[`threebody_tersoff.py`](https://github.com/eragasa/pypospack/blob/be453fa7191e55a0426f66e8b5b5b0b103c8b29d/pypospack/potential/threebody_tersoff.py)
independently corroborates the parameter sequence. Its exact hash and size are
selected in `sources/pypospack.toml`. It is not imported, executed, or treated
as a repair for the PyFlamestk source.

Parsing is closed and enumerated. `_external_potential_models`,
`_dependent_parameter_models`, `_qoi_models`, `_qoi_model_contract`, and
`_verify_implementation_spans` do not evaluate source expressions. Exact source
spans remain attached to every definition and implementation.

## References

These are the sources cited by the LAMMPS Tersoff page. The first four support
the unshifted Tersoff interpretation used here; the final two concern the
optional `shift` behavior and are listed for completeness, not implemented.

1. LAMMPS, [`pair_style tersoff` command](https://docs.lammps.org/pair_tersoff.html).
2. J. Tersoff, “New empirical approach for the structure and energy of covalent
   systems,” *Physical Review B* **37**, 6991–7000 (1988),
   [doi:10.1103/PhysRevB.37.6991](https://doi.org/10.1103/PhysRevB.37.6991).
3. J. Tersoff, “Modeling solid-state chemistry: Interatomic potentials for
   multicomponent systems,” *Physical Review B* **39**, 5566–5568 (1989),
   [doi:10.1103/PhysRevB.39.5566](https://doi.org/10.1103/PhysRevB.39.5566),
   and the [erratum](https://doi.org/10.1103/PhysRevB.41.3248.2), *Physical
   Review B* **41**, 3248 (1990).
4. J. Nord, K. Albe, P. Erhart, and K. Nordlund, “Modelling of compound
   semiconductors: analytical bond-order potential for gallium, nitrogen and
   gallium nitride,” *Journal of Physics: Condensed Matter* **15**, 5649–5662
   (2003),
   [doi:10.1088/0953-8984/15/32/324](https://doi.org/10.1088/0953-8984/15/32/324).
5. D. Mandelli, W. Ouyang, M. Urbakh, and O. Hod, “The Princess and the
   Nanoscale Pea: Long-Range Penetration of Surface Distortions into Layered
   Materials Stacks,” *ACS Nano* **13**, 7603–7609 (2019),
   [doi:10.1021/acsnano.9b00645](https://doi.org/10.1021/acsnano.9b00645).
6. W. Ouyang et al., “Mechanical and Tribological Properties of Layered
   Materials under High Pressure: Assessing the Importance of Many-Body
   Dispersion Effects,” *Journal of Chemical Theory and Computation* **16**,
   666–676 (2020),
   [doi:10.1021/acs.jctc.9b00908](https://doi.org/10.1021/acs.jctc.9b00908).
