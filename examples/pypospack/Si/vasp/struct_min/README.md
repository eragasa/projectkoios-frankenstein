# Silicon VASP structural-minimization example

This is the compact, runnable portion of the operator-provided `si_vasp/struct_min`
calculation. The text inputs and historical scheduler script are preserved byte-for-byte.
A clean local reproduction completed successfully with VASP 5.3.5; its final `CONTCAR`
and compact result record are retained under `expected/`.

The VASP `POTCAR` is deliberately not committed. Exact reproduction requires an
external file with SHA-256
`79d9987ad8750f624c4d6acb2a16d13abf6a777132adc04dc6c8399be72b42bb`.
The observed artifact identifies `PAW_PBE Si 05Jan2001`, `LEXCH=PE`, and
`ENMAX=245.345 eV`.

To run in an isolated workspace:

```bash
workspace="$(mktemp -d /tmp/si-vasp.XXXXXX)"
cp input/INCAR input/POSCAR input/KPOINTS "$workspace/"
cp "$VASP_POTCAR" "$workspace/POTCAR"
(
  cd "$workspace"
  OMP_NUM_THREADS=1 "$VASP_BIN" >stdout.log 2>stderr.log
)
```

Do not run `historical/runjob_si.pbs` locally. It records the original cluster-specific
module and scheduler invocation only.

A completed run demonstrates executable operation and numerical reproduction of this
finite input. It does not establish convergence, scientific validation, or suitability
as a production silicon reference.
