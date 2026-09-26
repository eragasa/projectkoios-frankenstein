# Silicon single-SCF convergence examples

Three convergence cases are maintained independently:

- [`k_points/`](k_points/): vary cubic k-point density at fixed wavefunction cutoff;
- [`encut/`](encut/): vary wavefunction cutoff at fixed cubic k-point density;
- [`cross/`](cross/): vary both coordinates on a Cartesian grid.

Each case contains separate `vasp`, `qe`, and `comparator` examples. VASP and QE use the common `dft_pw_scf` child workflow. Comparators reassess neighboring relative-energy changes under one shared policy and do not compare calculator-native absolute energy zeros.

Validate and display any backend campaign plan:

```bash
PYTHONPATH=src:. .venv/bin/python \
  examples/projectkoios/Si/single_scf/workflow/runner/plan.py \
  examples/projectkoios/Si/single_scf/convergence/k_points/qe/campaign.toml \
  --runner-config examples/projectkoios/Si/single_scf/workflow/runner/config/runner.toml
```

Run a comparator after independently producing two retained evidence JSON files:

```bash
PYTHONPATH=src:. .venv/bin/python \
  examples/projectkoios/Si/single_scf/workflow/runner/compare_convergence.py \
  examples/projectkoios/Si/single_scf/convergence/k_points/comparator/comparison.toml \
  --runner-config examples/projectkoios/Si/single_scf/workflow/runner/config/runner.toml \
  --left-evidence /path/to/qe-evidence.json \
  --right-evidence /path/to/vasp-evidence.json
```

Each evidence file has schema version `1`, a nonempty `evidence_id`, and an `observations` array. Every observation contains `mesh_density`, `wavefunction_cutoff_ev`, and `total_energy_ev_per_atom`. Evidence production and durable artifact identity remain outside this presentation-layer loader.
