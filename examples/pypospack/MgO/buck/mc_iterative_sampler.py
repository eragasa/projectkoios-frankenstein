from __future__ import annotations

import os
import secrets
import sys
from pathlib import Path

EXAMPLE_ROOT = Path(__file__).resolve().parent
VENDOR_ROOT = EXAMPLE_ROOT / "vendor"
sys.path.insert(0, os.fspath(VENDOR_ROOT))

from configuration import (  # noqa: E402
    ConfigurationError,
    ExecutionConfiguration,
    MgOBuckinghamConfiguration,
    configure_pypospack_legacy_yaml_loader,
    write_resolved_snapshot,
)
from mc_sampler_iterate import PyposmatIterativeSampler  # noqa: E402
from mpi4py import MPI  # noqa: E402

SOURCE_CONFIG_SHA256 = (
    "4fc039818280e080f8df18eaa2ccf0c6450a7b2265394931cda9e7c180a3c037"
)
SOURCE_REVISION = "be453fa7191e55a0426f66e8b5b5b0b103c8b29d"
SOURCE_TREE = "7ac9c9f255aa7731f39ce35a0e561fc113082a6f"


def _resolve_random_seed(scientific: MgOBuckinghamConfiguration) -> int:
    raw_seed = os.environ.get("PYPOSMAT_RANDOM_SEED")
    if raw_seed is not None:
        try:
            seed = int(raw_seed)
        except ValueError as error:
            raise ConfigurationError(
                "PYPOSMAT_RANDOM_SEED must be an integer"
            ) from error
        if seed < 0:
            raise ConfigurationError("PYPOSMAT_RANDOM_SEED must be non-negative")
        return seed
    if scientific.mc_seed is not None:
        return scientific.mc_seed
    return secrets.randbelow(2**31)


def main() -> None:
    work_directory = Path.cwd()
    source_config = work_directory / "data/pyposmat.config.in"
    scientific = MgOBuckinghamConfiguration.from_legacy_file(
        source_config,
        expected_sha256=SOURCE_CONFIG_SHA256,
    )
    scientific.validate_structure_files(work_directory)

    execution = ExecutionConfiguration.from_environment(
        work_directory=work_directory,
        data_directory="data",
        mpi_size=MPI.COMM_WORLD.Get_size(),
    )
    execution.validate(require_lammps=True)
    random_seed = _resolve_random_seed(scientific)

    write_resolved_snapshot(
        execution.data_directory / "pyposmat.resolved.json",
        scientific=scientific,
        execution=execution,
        source_revision=SOURCE_REVISION,
        source_tree=SOURCE_TREE,
        random_seed=random_seed,
    )

    configure_pypospack_legacy_yaml_loader()
    sampler = PyposmatIterativeSampler(
        configuration_filename=str(source_config),
        is_restart=execution.restart,
        log_to_stdout=execution.log_to_stdout,
    )
    sampler.data_directory = str(execution.data_directory)
    sampler.rv_seed = random_seed
    sampler.read_configuration_file()
    sampler.run_all()


if __name__ == "__main__":
    try:
        main()
    except ConfigurationError as error:
        raise SystemExit(f"configuration error: {error}") from error
