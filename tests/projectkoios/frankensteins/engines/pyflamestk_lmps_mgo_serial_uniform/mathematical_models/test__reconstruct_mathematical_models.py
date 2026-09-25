from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from projectkoios.frankensteins.engines.pyflamestk_lmps_mgo_serial_uniform import (
    EXAMPLE_ROOT,
    reconstruct_checkout,
    reconstruct_mathematical_models,
)
from projectkoios.frankensteins.mathematics import MathematicalModelKind

_CHECKOUT_VALUE = os.environ.get("PYFLAMESTK_CHECKOUT")
CHECKOUT = Path(_CHECKOUT_VALUE).resolve() if _CHECKOUT_VALUE else None


@unittest.skipUnless(CHECKOUT is not None, "PYFLAMESTK_CHECKOUT is not set")
class PyflamestkMgoMathematicalModelsTest(unittest.TestCase):
    def test_extracts_the_example_selected_models_in_source_order(self) -> None:
        assert CHECKOUT is not None
        catalog = reconstruct_mathematical_models(CHECKOUT)

        self.assertEqual(len(catalog.models), 11)
        self.assertEqual(len(catalog.external_models), 1)
        self.assertEqual(
            tuple(model.name for model in catalog.models),
            (
                "chrg_O",
                "MgO_NaCl.a0",
                "MgO_NaCl.c11",
                "MgO_NaCl.c12",
                "MgO_NaCl.c44",
                "MgO_NaCl.B",
                "MgO_NaCl.G",
                "MgO_NaCl.fr_a",
                "MgO_NaCl.fr_c",
                "MgO_NaCl.sch",
                "MgO_NaCl.001s",
            ),
        )
        self.assertEqual(
            catalog.model("MgO_NaCl.B").kind,
            MathematicalModelKind.CUBIC_BULK_MODULUS,
        )
        self.assertEqual(
            catalog.model("MgO_NaCl.G").kind,
            MathematicalModelKind.TETRAGONAL_SHEAR_MODULUS,
        )
        self.assertEqual(
            catalog.model("MgO_NaCl.fr_a").kind,
            MathematicalModelKind.DEFECT_FORMATION_ENERGY,
        )
        self.assertEqual(
            catalog.model("MgO_NaCl.001s").kind,
            MathematicalModelKind.SURFACE_ENERGY,
        )
        buckingham = catalog.external_models[0]
        self.assertEqual(buckingham.name, "MgO.buckingham")
        self.assertEqual(buckingham.backend_model, "lammps.buck_coul_long")
        self.assertEqual(buckingham.species, ("Mg", "O"))
        self.assertEqual(
            buckingham.pair_interactions,
            (("Mg", "O"), ("O", "O"), ("Mg", "Mg")),
        )
        self.assertFalse(buckingham.evaluation_supported)
        self.assertFalse(buckingham.scientific_validation_claimed)

    def test_evaluates_only_closed_finite_arithmetic_models(self) -> None:
        assert CHECKOUT is not None
        catalog = reconstruct_mathematical_models(CHECKOUT)

        self.assertEqual(
            catalog.model("chrg_O").evaluate({"chrg_Mg": 2.0}),
            -2.0,
        )
        self.assertEqual(
            catalog.model("MgO_NaCl.a0").evaluate({"MgO_NaCl.a0": 4.246}),
            4.246,
        )
        elastic = {
            "MgO_NaCl.c11": 277.0,
            "MgO_NaCl.c12": 91.67,
            "MgO_NaCl.c44": 144.01,
        }
        self.assertAlmostEqual(
            catalog.model("MgO_NaCl.B").evaluate(elastic),
            153.44666666666666,
        )
        self.assertAlmostEqual(
            catalog.model("MgO_NaCl.G").evaluate(elastic),
            92.665,
        )
        self.assertAlmostEqual(
            catalog.model("MgO_NaCl.fr_a").evaluate(
                {
                    "MgO_NaCl_fr_a.E_min_pos": -100.0,
                    "MgO_NaCl_fr_a.n_atoms": 63,
                    "MgO_NaCl.E_min": -102.0,
                    "MgO_NaCl.n_atoms": 64,
                }
            ),
            0.40625,
        )
        self.assertAlmostEqual(
            catalog.model("MgO_NaCl.001s").evaluate(
                {
                    "MgO_NaCl_001_s.E_min_pos": -90.0,
                    "MgO_NaCl_001_s.a1_min_pos": 4.0,
                    "MgO_NaCl_001_s.a2_min_pos": 5.0,
                    "MgO_NaCl_001_s.n_atoms": 56,
                    "MgO_NaCl.E_min": -102.0,
                    "MgO_NaCl.n_atoms": 64,
                }
            ),
            -0.01875,
        )

    def test_preserves_the_source_declared_unused_c44_dependency(self) -> None:
        assert CHECKOUT is not None
        catalog = reconstruct_mathematical_models(CHECKOUT)
        bulk = catalog.model("MgO_NaCl.B")

        self.assertEqual(
            tuple(item.source_variable for item in bulk.unused_required_inputs),
            ("MgO_NaCl.c44",),
        )
        first = bulk.evaluate(
            {
                "MgO_NaCl.c11": 277.0,
                "MgO_NaCl.c12": 91.67,
                "MgO_NaCl.c44": 0.0,
            }
        )
        second = bulk.evaluate(
            {
                "MgO_NaCl.c11": 277.0,
                "MgO_NaCl.c12": 91.67,
                "MgO_NaCl.c44": 1_000.0,
            }
        )
        self.assertEqual(first, second)

    def test_rejects_missing_extra_nonfinite_and_zero_denominator_inputs(self) -> None:
        assert CHECKOUT is not None
        catalog = reconstruct_mathematical_models(CHECKOUT)
        bulk = catalog.model("MgO_NaCl.B")
        defect = catalog.model("MgO_NaCl.fr_a")

        with self.assertRaisesRegex(ValueError, "exactly match"):
            bulk.evaluate(
                {
                    "MgO_NaCl.c11": 277.0,
                    "MgO_NaCl.c12": 91.67,
                }
            )
        with self.assertRaisesRegex(ValueError, "exactly match"):
            bulk.evaluate(
                {
                    "MgO_NaCl.c11": 277.0,
                    "MgO_NaCl.c12": 91.67,
                    "MgO_NaCl.c44": 144.01,
                    "unexpected": 1.0,
                }
            )
        with self.assertRaisesRegex(ValueError, "finite"):
            bulk.evaluate(
                {
                    "MgO_NaCl.c11": float("nan"),
                    "MgO_NaCl.c12": 91.67,
                    "MgO_NaCl.c44": 144.01,
                }
            )
        with self.assertRaisesRegex(ValueError, "cannot be zero"):
            defect.evaluate(
                {
                    "MgO_NaCl_fr_a.E_min_pos": -100.0,
                    "MgO_NaCl_fr_a.n_atoms": 63,
                    "MgO_NaCl.E_min": -102.0,
                    "MgO_NaCl.n_atoms": 0,
                }
            )

    def test_catalog_and_recipe_identities_are_stable_and_path_private(self) -> None:
        assert CHECKOUT is not None
        first = reconstruct_checkout(CHECKOUT)
        second = reconstruct_checkout(CHECKOUT)

        self.assertEqual(
            first.mathematical_models.catalog_id,
            second.mathematical_models.catalog_id,
        )
        self.assertEqual(first.recipe_id, second.recipe_id)
        payload = json.loads(first.to_json())
        self.assertEqual(
            payload["mathematical_models"]["catalog_id"],
            first.mathematical_models.catalog_id,
        )
        serialized = first.to_json()
        self.assertNotIn("/Users/", serialized)
        self.assertNotIn("/home/", serialized)
        self.assertFalse(
            payload["mathematical_models"]["models"][0]["scientific_validation_claimed"]
        )

    def test_recipe_rejects_a_catalog_from_different_provenance(self) -> None:
        assert CHECKOUT is not None
        recipe = reconstruct_checkout(CHECKOUT)
        mismatched = replace(
            recipe.mathematical_models,
            source_component="other",
        )

        with self.assertRaisesRegex(ValueError, "provenance must match"):
            replace(recipe, mathematical_models=mismatched)

    def test_rejects_mutated_mathematical_source_evidence(self) -> None:
        assert CHECKOUT is not None
        relevant_paths = (
            "pyflamestk/qoi.py",
            "pyflamestk/pyposmat.py",
            "pyflamestk/lammps.py",
            f"{EXAMPLE_ROOT}/pyposmat.qoi",
            f"{EXAMPLE_ROOT}/pyposmat.potential",
        )
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "checkout"
            for relative_path in relevant_paths:
                destination = copy / relative_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(CHECKOUT / relative_path, destination)
            target = copy / "pyflamestk/qoi.py"
            target.write_text(
                target.read_text(encoding="utf-8") + "\n# mutation\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "source mismatch"):
                reconstruct_mathematical_models(copy)


if __name__ == "__main__":
    unittest.main()
