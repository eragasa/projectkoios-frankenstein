from __future__ import annotations

import os
import unittest
from pathlib import Path

from projectkoios.frankensteins.engines.pyflamestk_examples import (
    ENGINE_BINDINGS,
    reconstruct_example_engine,
)

_CHECKOUT_VALUE = os.environ.get("PYFLAMESTK_CHECKOUT")
CHECKOUT = Path(_CHECKOUT_VALUE).resolve() if _CHECKOUT_VALUE else None


@unittest.skipUnless(CHECKOUT is not None, "PYFLAMESTK_CHECKOUT is not set")
class ReconstructExampleEngineTest(unittest.TestCase):
    def test_reconstructs_every_supported_source_example(self) -> None:
        assert CHECKOUT is not None
        recipes = []
        for binding in ENGINE_BINDINGS:
            if binding.status != "reconstructable":
                continue
            with self.subTest(engine=binding.engine_name):
                recipe = reconstruct_example_engine(CHECKOUT, binding.engine_name)
                self.assertEqual(recipe.engine_name, binding.engine_name)
                self.assertEqual(recipe.source_example_root, binding.example_root)
                self.assertFalse(recipe.execution_authorized)
                self.assertGreaterEqual(len(recipe.integrations), 1)
                self.assertGreaterEqual(len(recipe.mathematical_models.models), 10)
                self.assertNotIn(str(CHECKOUT), recipe.to_json())
                recipes.append(recipe)

        self.assertEqual(len(recipes), 16)
        self.assertEqual(len({recipe.recipe_id for recipe in recipes}), 16)

    def test_reconstructs_the_historical_file_sampling_variant(self) -> None:
        assert CHECKOUT is not None
        recipe = reconstruct_example_engine(
            CHECKOUT,
            "pyflamestk-legacy-mgo-sample-file",
        )

        self.assertEqual(len(recipe.mathematical_models.models), 10)
        self.assertEqual(len(recipe.integrations), 1)
        lammps = recipe.integrations[0].to_dict()["payload"]
        self.assertEqual(
            lammps["templates"][0]["command_intent"]["arguments"],
            [
                "-i",
                "in.single_point",
            ],
        )
        self.assertEqual(lammps["structures"][0]["atom_count"], 8)
        self.assertEqual(lammps["structures"][0]["atom_style"], "charge")
        self.assertIn(
            "historical_file_type_typo",
            {warning.code for warning in recipe.warnings},
        )

    def test_reconstructs_the_tersoff_declaration_with_source_warnings(self) -> None:
        assert CHECKOUT is not None
        recipe = reconstruct_example_engine(
            CHECKOUT,
            "pyflamestk-si-tersoff-si-serial-pareto",
        )

        tersoff = recipe.mathematical_models.external_models[0]
        self.assertEqual(tersoff.backend_model, "lammps.tersoff")
        self.assertEqual(tersoff.species, ("Si",))
        self.assertEqual(tersoff.pair_interactions, ())
        self.assertEqual(tersoff.triplet_interactions, (("Si", "Si", "Si"),))
        self.assertEqual(
            tersoff.parameter_variables,
            tuple(
                f"SiSiSi_{name}"
                for name in (
                    "m",
                    "gamma",
                    "lambda3",
                    "c",
                    "d",
                    "costheta0",
                    "n",
                    "beta",
                    "lambda2",
                    "B",
                    "R",
                    "D",
                    "lambda1",
                    "A",
                )
            ),
        )
        self.assertTrue(
            any(
                "docs.lammps.org/pair_tersoff.html" in item
                for item in tersoff.references
            )
        )
        self.assertTrue(any("PhysRevB.37.6991" in item for item in tersoff.references))
        warning_codes = {warning.code for warning in recipe.warnings}
        self.assertIn("historical_tersoff_implementation_incomplete", warning_codes)
        self.assertIn("potential_structure_species_mismatch", warning_codes)

    def test_refuses_each_explicitly_blocked_source_example(self) -> None:
        assert CHECKOUT is not None
        blocked = tuple(
            binding for binding in ENGINE_BINDINGS if binding.status == "blocked"
        )
        self.assertEqual(len(blocked), 1)
        for binding in blocked:
            with (
                self.subTest(engine=binding.engine_name),
                self.assertRaisesRegex(ValueError, "is blocked"),
            ):
                reconstruct_example_engine(CHECKOUT, binding.engine_name)


if __name__ == "__main__":
    unittest.main()
