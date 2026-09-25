# Silicon SCF input projections

These maintained examples construct a unit-aware two-atom primitive silicon `PwDftSimulation` with `CalculationType.scf`. The QE and VASP branches project the same semantic calculation type and equivalent `UnitCell` values into calculator-specific input models.

- [`qe/scf`](qe/scf/README.md) generates `pw.in`, including structure cards derived from `UnitCell`.
- [`vasp/scf`](vasp/scf/README.md) generates INCAR calculation fields through `VaspCalculationProjector` and POSCAR through `PoscarWriter`.
- [`plot_unit_cell.py`](plot_unit_cell.py) renders the primitive cell, direct lattice vectors, and atomic basis as a self-contained interactive Plotly HTML document.

Install the optional visualization dependency and generate the plot:

```bash
uv pip install --python .venv/bin/python 'plotly>=6.5,<7'
.venv/bin/python examples/projectkoios/Si/scf/plot_unit_cell.py \
  --output workspace/results/si-scf-example/si-primitive-cell.html
```

Open the resulting HTML in a browser to rotate, pan, zoom, and inspect coordinates.

The examples demonstrate deterministic input assembly. They do not establish cross-calculator numerical equivalence, pseudopotential equivalence, convergence, or scientific validation.
