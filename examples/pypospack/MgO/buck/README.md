# MgO Buckingham iterative sampler

This directory maintains a provenance-bound representation of the PyPosPack MgO
Buckingham iterative-sampling example. In the target architecture this workflow
is a multi-objective optimizer operating on a potential-optimization problem;
see the [architecture documentation](../../../../docs/architecture/index.md).

## Historical runtime boundary

`vendor/pypospack/qoi.py` and the complete `vendor/pypospack/qois/` package are
unchanged committed source blobs used for QOI conformance. The locally adapted
`vendor/pypospack/__init__.py` composes that partial package with non-QOI modules
from the exact pinned PyPosPack dependency. The launcher gives this vendored QOI
runtime import precedence.

The selection is declared in `VENDORING.toml`. From the repository root, verify
or reproduce it using an operator-provided checkout:

```bash
python3.14 tools/vendor_source_selection.py \
  examples/pypospack/MgO/buck/VENDORING.toml \
  --checkout "$PYPOSPACK_CHECKOUT" --check

python3.14 tools/vendor_source_selection.py \
  examples/pypospack/MgO/buck/VENDORING.toml \
  --checkout "$PYPOSPACK_CHECKOUT" --sync
```

The tool reads committed Git objects only. It does not execute the checkout or
change a source pin.

## Configuration layers

1. `data/pyposmat.config.in` is an unchanged upstream input. Its SHA-256 digest
   is checked before parsing and it must never be rewritten.
2. `configuration.py` safely decodes the one historical `OrderedDict` YAML tag,
   validates the scientific configuration, and models execution settings
   separately.
3. `mc_iterative_sampler.py` resolves the source and execution configurations,
   writes `data/pyposmat.resolved.json`, then invokes the vendored
   `PyposmatIterativeSampler` implementation in `mc_sampler_iterate.py`, with
   QOI imports resolved through the provenance-bound partial package.

The resolved snapshot records the source revision and tree, source input hash,
explicit random seed, resolved paths, MPI size, and LAMMPS identity supplied by
the operator. It is generated run state and is not source provenance.

## Execution inputs

Set an explicit executable and, optionally, its version and random seed:

```bash
export LAMMPS_BIN=/absolute/path/to/lmp
export LAMMPS_VERSION="operator-reported version"
export PYPOSMAT_RANDOM_SEED=1234
cd examples/pypospack/MgO/buck
../../../../.venv/bin/python mc_iterative_sampler.py
```

Run the command with `examples/pypospack/MgO/buck` as the working directory.
The launcher validates all source structures and execution settings before
calling the sampler. No LAMMPS executable is bundled or authorized by the
provenance records.
