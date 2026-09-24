from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from projectkoios.frankensteins.engines.pyflamestk_lmps_mgo_serial_uniform import (
    EXAMPLE_ROOT,
    SOURCE_REPOSITORY_URL,
    SOURCE_REVISION,
    SOURCE_TREE,
    reconstruct_checkout,
)

_CHECKOUT_VALUE = os.environ.get("PYFLAMESTK_CHECKOUT")
CHECKOUT = Path(_CHECKOUT_VALUE).resolve() if _CHECKOUT_VALUE else None


@unittest.skipUnless(CHECKOUT is not None, "PYFLAMESTK_CHECKOUT is not set")
class PyflamestkMgoFrankensteinTest(unittest.TestCase):
    def test_reconstructs_stable_execution_disabled_recipe(self) -> None:
        assert CHECKOUT is not None
        first = reconstruct_checkout(CHECKOUT)
        second = reconstruct_checkout(CHECKOUT)

        self.assertEqual(first, second)
        self.assertEqual(first.recipe_id, second.recipe_id)
        self.assertEqual(len(first.source_files), 29)
        self.assertFalse(first.execution_authorized)
        self.assertEqual(first.source_repository_url, SOURCE_REPOSITORY_URL)
        self.assertEqual(first.source_revision, SOURCE_REVISION)
        self.assertEqual(first.source_tree, SOURCE_TREE)
        self.assertEqual(first.source_example_root, EXAMPLE_ROOT)

        settings = {(item.key, item.values) for item in first.settings}
        self.assertIn(("n_simulations", ("100",)), settings)
        self.assertIn(("sampler_type", ("uniform",)), settings)
        self.assertIn(("is_restart", ("true",)), settings)
        self.assertNotIn("lmps_bin", {item.key for item in first.settings})
        self.assertNotIn("lmps_exe_script", {item.key for item in first.settings})

        integrations = {
            item.integration: json.loads(item.payload_json)
            for item in first.integrations
        }
        self.assertEqual(
            set(integrations),
            {"integrations.lammps", "integrations.vasp"},
        )
        lammps = integrations["integrations.lammps"]
        self.assertFalse(lammps["external_execution_authorized"])
        self.assertEqual(len(lammps["templates"]), 4)
        for template in lammps["templates"]:
            intent = template["command_intent"]
            self.assertEqual(intent["program"], "lammps")
            self.assertEqual(intent["executable_environment_variable"], "LAMMPS_BIN")
            self.assertFalse(intent["execution_authorized"])

        vasp = integrations["integrations.vasp"]
        self.assertFalse(vasp["external_execution_authorized"])
        self.assertFalse(vasp["pseudopotential_selection_authorized"])
        self.assertEqual(len(vasp["structures"]), 5)
        self.assertEqual(
            {structure["coordinate_mode"] for structure in vasp["structures"]},
            {"direct"},
        )
        serialized = first.to_json()
        self.assertNotIn(str(CHECKOUT), serialized)

    def test_detects_upstream_source_mutation(self) -> None:
        assert CHECKOUT is not None
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "checkout"
            shutil.copytree(CHECKOUT, copy, ignore=shutil.ignore_patterns(".git"))
            target = copy / EXAMPLE_ROOT / "pyposmat.qoi"
            target.write_text(
                target.read_text(encoding="utf-8") + "\n# mutation\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                reconstruct_checkout(copy)

    def test_vasp_observations_preserve_exact_atom_counts(self) -> None:
        assert CHECKOUT is not None
        recipe = reconstruct_checkout(CHECKOUT)
        vasp = next(
            json.loads(item.payload_json)
            for item in recipe.integrations
            if item.integration == "integrations.vasp"
        )
        unit = next(
            structure
            for structure in vasp["structures"]
            if structure["name"] == "MgO_NaCl"
        )
        self.assertEqual(unit["element_symbols"], ["Mg", "O"])
        self.assertEqual(unit["element_counts"], [4, 4])
        self.assertEqual(unit["coordinate_count"], 8)
        self.assertFalse(unit["calculator_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
