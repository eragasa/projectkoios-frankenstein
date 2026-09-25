# Silicon Quantum ESPRESSO SCF input

Generate the committed input into another directory:

```bash
PYTHONPATH=src .venv/bin/python examples/projectkoios/Si/scf/qe/scf/run.py \
  --output /tmp/projectkoios-si-qe-scf
```

`run.py` selects `CalculationType.scf` once on `PwDftSimulation`. `QePwInputFileAssembler` projects it to `&CONTROL calculation='scf'` and generates `ATOMIC_POSITIONS (crystal)` and `CELL_PARAMETERS (angstrom)` from the simulation's unit-aware `UnitCell`. The example supplies the remaining `&SYSTEM`, `&ELECTRONS`, `ATOMIC_SPECIES`, and `K_POINTS` content explicitly.

Execution resolves SSSP 1.3.0 PBE efficiency `Si.pbe-n-rrkjus_psl.1.0.0.UPF` directly from `~/opt/pseudopotentials`, verifies its exact identity, and stages it under that basename. The input uses the SSSP-recommended `ecutwfc = 30 Ry` and `ecutrho = 240 Ry`. The committed file is an assembly fixture, not evidence of convergence or a completed Quantum ESPRESSO calculation.
