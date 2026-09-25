# Silicon VASP SCF inputs

Generate the committed inputs into another directory:

```bash
PYTHONPATH=src .venv/bin/python examples/projectkoios/Si/scf/vasp/scf/run.py \
  --output /tmp/projectkoios-si-vasp-scf
```

`run.py` selects `CalculationType.scf` once on `PwDftSimulation`. `VaspCalculationProjector` projects it to `IBRION=-1` and `NSW=0`; the example supplies the remaining electronic settings. `PoscarWriter` generates POSCAR from the same simulation's unit-aware `UnitCell`. `calculation-projection.json` preserves the alignment classification and qualification.

The example deliberately does not copy or generate POTCAR. Execution resolves the compatible licensed silicon POTCAR from the local `storage/pseudopotentials/` repository. These files demonstrate deterministic assembly and do not establish convergence or a completed VASP calculation.
