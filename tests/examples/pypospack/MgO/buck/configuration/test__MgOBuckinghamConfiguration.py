from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from tests.support.repository_root import REPOSITORY_ROOT

EXAMPLE_ROOT = REPOSITORY_ROOT / "examples/pypospack/MgO/buck"
CONFIGURATION_PATH = EXAMPLE_ROOT / "configuration.py"
SOURCE_CONFIG_PATH = EXAMPLE_ROOT / "data/pyposmat.config.in"
SOURCE_CONFIG_SHA256 = (
    "4fc039818280e080f8df18eaa2ccf0c6450a7b2265394931cda9e7c180a3c037"
)


def _load_configuration_module() -> ModuleType:
    module_name = "projectkoios_example_mgo_buck_configuration"
    spec = importlib.util.spec_from_file_location(module_name, CONFIGURATION_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load MgO Buckingham configuration module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    previous_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous_dont_write_bytecode
    return module


configuration = _load_configuration_module()
ConfigurationError = configuration.ConfigurationError
ExecutionConfiguration = configuration.ExecutionConfiguration
MgOBuckinghamConfiguration = configuration.MgOBuckinghamConfiguration


class MgOBuckinghamConfigurationTest(unittest.TestCase):
    def load_source(self):
        return MgOBuckinghamConfiguration.from_legacy_file(
            SOURCE_CONFIG_PATH,
            expected_sha256=SOURCE_CONFIG_SHA256,
        )

    def test_loads_the_unchanged_historical_configuration(self) -> None:
        source = self.load_source()

        self.assertEqual(source.source_sha256, SOURCE_CONFIG_SHA256)
        self.assertEqual(len(source.qois), 10)
        self.assertEqual(len(source.structures), 5)
        self.assertEqual(source.potential.potential_type, "buckingham")
        self.assertEqual(source.potential.symbols, ("Mg", "O"))
        self.assertEqual(len(source.iterations), 20)
        self.assertEqual(source.iterations[0].mode, "parametric")
        self.assertTrue(
            all(iteration.mode == "kde" for iteration in source.iterations[1:])
        )
        self.assertTrue(
            all(iteration.n_samples == 100 for iteration in source.iterations)
        )
        self.assertIsNone(source.mc_seed)
        self.assertEqual(len(source.parameter_distributions), 11)
        self.assertEqual(len(source.parameter_constraints), 6)

    def test_rejects_a_source_identity_mismatch(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "SHA-256"):
            MgOBuckinghamConfiguration.from_legacy_file(
                SOURCE_CONFIG_PATH,
                expected_sha256="0" * 64,
            )

    def test_rejects_arbitrary_python_yaml_tags(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unsafe.yaml"
            path.write_text(
                "!!python/object/apply:os.system ['echo must-not-run']\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ConfigurationError, "invalid YAML"):
                MgOBuckinghamConfiguration.from_legacy_file(path)

    def test_rejects_the_known_broken_cluster_mode(self) -> None:
        source_text = SOURCE_CONFIG_PATH.read_text(encoding="utf-8")
        modified = source_text.replace("- parametric", "- kde_w_clusters", 1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.yaml"
            path.write_text(modified, encoding="utf-8")
            with self.assertRaisesRegex(ConfigurationError, "undefined _mc_config"):
                MgOBuckinghamConfiguration.from_legacy_file(path)

    def test_rejects_structure_path_traversal(self) -> None:
        source_text = SOURCE_CONFIG_PATH.read_text(encoding="utf-8")
        modified = source_text.replace("- structure_db", "- ../structure_db", 1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "traversal.yaml"
            path.write_text(modified, encoding="utf-8")
            with self.assertRaisesRegex(ConfigurationError, "contained relative path"):
                MgOBuckinghamConfiguration.from_legacy_file(path)

    def test_rejects_an_incomplete_buckingham_parameter_set(self) -> None:
        source_text = SOURCE_CONFIG_PATH.read_text(encoding="utf-8")
        modified = source_text.replace("- - OO_C", "- - unexpected_C", 1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "parameters.yaml"
            path.write_text(modified, encoding="utf-8")
            with self.assertRaisesRegex(ConfigurationError, "Buckingham parameters"):
                MgOBuckinghamConfiguration.from_legacy_file(path)

    def test_rejects_executable_constraint_syntax(self) -> None:
        source_text = SOURCE_CONFIG_PATH.read_text(encoding="utf-8")
        modified = source_text.replace(
            "- chrg_Mg > 0.\n",
            "- __import__('os').system(1)\n",
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "constraint.yaml"
            path.write_text(modified, encoding="utf-8")
            with self.assertRaisesRegex(ConfigurationError, "must be a comparison"):
                MgOBuckinghamConfiguration.from_legacy_file(path)

    def test_validates_the_structure_database(self) -> None:
        source = self.load_source()
        source.validate_structure_files(EXAMPLE_ROOT)
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaisesRegex(ConfigurationError, "missing structure files"),
        ):
            source.validate_structure_files(directory)

    def test_execution_configuration_requires_an_explicit_lammps_binary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work_directory = Path(directory)
            execution = ExecutionConfiguration(
                work_directory=work_directory,
                data_directory=Path("data"),
            )
            execution.validate(require_lammps=False)
            with self.assertRaisesRegex(ConfigurationError, "LAMMPS_BIN is required"):
                execution.validate(require_lammps=True)

    def test_execution_configuration_reads_environment_without_running_lammps(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work_directory = Path(directory)
            lammps = work_directory / "lmp"
            lammps.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            lammps.chmod(0o755)
            with patch.dict(
                os.environ,
                {
                    "LAMMPS_BIN": os.fspath(lammps),
                    "LAMMPS_VERSION": "test-version",
                },
                clear=False,
            ):
                execution = ExecutionConfiguration.from_environment(
                    work_directory=work_directory,
                    mpi_size=2,
                    restart=True,
                    log_to_stdout=False,
                )
            execution.validate()
            self.assertEqual(execution.lammps_binary, lammps.resolve())
            self.assertEqual(execution.lammps_version, "test-version")
            self.assertEqual(execution.mpi_size, 2)
            self.assertTrue(execution.restart)
            self.assertFalse(execution.log_to_stdout)

    def test_writes_a_resolved_run_snapshot(self) -> None:
        source = self.load_source()
        with tempfile.TemporaryDirectory() as directory:
            work_directory = Path(directory)
            execution = ExecutionConfiguration(
                work_directory=work_directory,
                data_directory=Path("data"),
                mpi_size=1,
            )
            destination = work_directory / "data/resolved.json"
            configuration.write_resolved_snapshot(
                destination,
                scientific=source,
                execution=execution,
                source_revision="revision",
                source_tree="tree",
                random_seed=1234,
            )
            document = json.loads(destination.read_text(encoding="utf-8"))

        self.assertEqual(document["source"]["revision"], "revision")
        self.assertEqual(document["source"]["tree"], "tree")
        self.assertEqual(document["random_seed"], 1234)
        self.assertEqual(document["scientific"]["source_sha256"], SOURCE_CONFIG_SHA256)
        self.assertEqual(document["execution"]["mpi_size"], 1)

    def test_configures_the_pinned_pypospack_loader_for_the_exact_legacy_tag(
        self,
    ) -> None:
        from pypospack.pyposmat.data import PyposmatConfigurationFile

        configuration.configure_pypospack_legacy_yaml_loader()
        parsed = PyposmatConfigurationFile()
        parsed.read(filename=os.fspath(SOURCE_CONFIG_PATH))
        self.assertEqual(parsed.n_iterations, 20)


if __name__ == "__main__":
    unittest.main()
