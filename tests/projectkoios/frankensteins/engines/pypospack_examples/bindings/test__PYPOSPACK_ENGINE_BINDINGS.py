from __future__ import annotations

import unittest
from collections import Counter

from projectkoios.frankensteins.engines.pypospack_examples import (
    ENGINE_BINDINGS,
    SOURCE_EXAMPLE_TREES,
    engine_binding,
)


class PypospackExampleEngineBindingsTest(unittest.TestCase):
    def test_catalogs_every_bounded_engine_shaped_source_example(self) -> None:
        self.assertEqual(len(ENGINE_BINDINGS), 31)
        self.assertEqual(len(SOURCE_EXAMPLE_TREES), 31)
        self.assertEqual(sum(len(item.entrypoints) for item in ENGINE_BINDINGS), 37)
        self.assertEqual(
            Counter(item.execution_surface for item in ENGINE_BINDINGS),
            Counter({"pyposmat": 23, "vasp": 6, "lammps": 2}),
        )
        for binding in ENGINE_BINDINGS:
            with self.subTest(engine=binding.engine_name):
                self.assertIs(engine_binding(binding.engine_name), binding)
                self.assertEqual(
                    SOURCE_EXAMPLE_TREES[binding.example_root],
                    binding.example_tree,
                )

    def test_rejects_an_unknown_engine_name(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown PyPosPack"):
            engine_binding("pypospack-unknown")


if __name__ == "__main__":
    unittest.main()
