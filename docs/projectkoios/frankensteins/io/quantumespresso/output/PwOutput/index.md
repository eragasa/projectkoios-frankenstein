# `PwOutput`

Immutable selected output observations:

- `program_version` records the reported PWSCF version;
- `job_completed` records the `JOB DONE.` marker;
- `scf_converged` records the positive convergence marker;
- `total_energy_ry` retains the final represented total energy in Ry;
- `wavefunction_cutoff_ry` retains the represented cutoff in Ry;
- `pressure_kbar` retains final represented pressure in kbar;
- `atom_count` and `k_point_count` retain reported counts; and
- `scf_iteration_count` counts represented SCF iteration rows.

These are raw software observations, not accepted scientific results.
