# Retained bulk-silicon QE SCF convergence replay

This example retains the complete 36-calculation `actual1` Quantum ESPRESSO grid rather than selecting a subset after observing the result. It replays native input, standard-output, standard-error, and execution records without invoking `pw.x`.

## Evidence

`evidence/manifest.json` conforms to the closed `evidence/schema.json` contract and identifies:

- the reviewed `Si.PrimitiveUnitCell` structure record;
- the exact QE 7.5 executable hash, size, and reported source revision;
- the exact Si UPF hash, size, and scientific metadata;
- the complete bounded convergence policy;
- all 30 initial-grid and 6 adaptive-extension coordinates;
- every retained artifact's SHA-256 identity and byte size; and
- the structured IEEE warnings preserved from every successful calculation.

The executable and pseudopotential bytes are identified but are not copied into this repository. The native calculation artifacts are retained verbatim under `evidence/artifacts/`.

## Replay

From the repository root, run:

```bash
PYTHONPATH=src .venv/bin/python -m \
  examples.projectkoios.Si.bulk.qe_wannier90.scf_convergence.replay
```

The replay verifies all declared hashes and sizes, checks each retained input against the structure, pseudopotential, mesh, and cutoff declarations, parses every native output through the maintained QE parsers, reproduces the six-point adaptive extension, and passes all 36 observations through the maintained calculator-neutral convergence assessor and controller.

The retained outcome is a policy acceptance at mesh density `14` and wavefunction cutoff `40 Ry`. The final neighboring-point deltas are:

- k-point edge: `0.2876923810788412` and `0.05986504976362994 meV/atom`;
- cutoff edge: `0.5384453053522975` and `0.31735279210920453 meV/atom`.

## Qualification

This is finite-grid total-energy convergence under the declared policy. It does not establish force, stress, band, NSCF, Wannier, effective-mass, dopant, or charged-defect convergence. The outputs were produced by an ignored local prototype whose Python source has no committed identity; the exact native inputs, outputs, execution records, calculator identity, and pseudopotential identity are retained or declared independently.
