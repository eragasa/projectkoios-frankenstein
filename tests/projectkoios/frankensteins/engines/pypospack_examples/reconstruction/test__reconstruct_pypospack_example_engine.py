from __future__ import annotations

import os
import unittest
from pathlib import Path

from projectkoios.frankensteins.engines.pypospack_examples import (
    ENGINE_BINDINGS,
    reconstruct_example_engine,
)

_CHECKOUT_VALUE = os.environ.get("PYPOSPACK_CHECKOUT")
CHECKOUT = Path(_CHECKOUT_VALUE).resolve() if _CHECKOUT_VALUE else None


@unittest.skipUnless(CHECKOUT is not None, "PYPOSPACK_CHECKOUT is not set")
class ReconstructPypospackExampleEngineTest(unittest.TestCase):
    def test_reconstructs_every_bounded_source_example(self) -> None:
        assert CHECKOUT is not None
        reconstructions = []
        for binding in ENGINE_BINDINGS:
            with self.subTest(engine=binding.engine_name):
                reconstruction = reconstruct_example_engine(
                    CHECKOUT,
                    binding.engine_name,
                )
                self.assertEqual(reconstruction.engine_name, binding.engine_name)
                self.assertEqual(
                    reconstruction.source_example_root,
                    binding.example_root,
                )
                self.assertFalse(reconstruction.execution_authorized)
                self.assertFalse(reconstruction.scientific_validation_claimed)
                self.assertNotIn(str(CHECKOUT), reconstruction.to_json())
                reconstructions.append(reconstruction)

        self.assertEqual(len(reconstructions), 31)
        self.assertEqual(
            len({item.reconstruction_id for item in reconstructions}),
            31,
        )

    def test_records_the_legacy_ordereddict_yaml_without_loading_it(self) -> None:
        assert CHECKOUT is not None
        reconstruction = reconstruct_example_engine(
            CHECKOUT,
            "pypospack-mgo-buck-iterative-sampler",
        )

        config = next(
            item
            for item in reconstruction.source_files
            if item.relative_path == "data/pyposmat.config.in"
        )
        self.assertGreater(config.byte_size, 0)
        self.assertEqual(
            reconstruction.integration.to_dict()["payload"][
                "historical_entrypoints_executed"
            ],
            False,
        )

    def test_records_backend_boundaries_without_authorizing_them(self) -> None:
        assert CHECKOUT is not None
        examples = {
            "pypospack-mgo-buck-lammps-neb": "lammps",
            "pypospack-ni-vasp-test": "vasp",
            "pypospack-si-tersoff": "pyposmat",
        }
        for engine_name, expected_surface in examples.items():
            with self.subTest(engine=engine_name):
                reconstruction = reconstruct_example_engine(CHECKOUT, engine_name)
                payload = reconstruction.integration.to_dict()["payload"]
                self.assertEqual(payload["execution_surface"], expected_surface)
                self.assertFalse(payload["external_execution_authorized"])
                self.assertFalse(payload["optimizer_execution_authorized"])
                self.assertFalse(payload["scheduler_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
