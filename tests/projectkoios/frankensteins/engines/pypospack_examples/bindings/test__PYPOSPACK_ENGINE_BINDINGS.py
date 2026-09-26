from __future__ import annotations

import unittest
from collections import Counter

from projectkoios.frankensteins.engines.pypospack_examples import (
    bindings as pypospack_bindings,
)


class PypospackExampleEngineBindingsTest(unittest.TestCase):
    def test__ENGINE_BINDINGS__catalog_every_bounded_source_example(self) -> None:
        self.assertEqual(len(pypospack_bindings.ENGINE_BINDINGS), 31)
        self.assertEqual(len(pypospack_bindings.SOURCE_EXAMPLE_TREES), 31)
        self.assertEqual(
            sum(len(item.entrypoints) for item in pypospack_bindings.ENGINE_BINDINGS),
            37,
        )
        self.assertEqual(
            Counter(
                item.execution_surface for item in pypospack_bindings.ENGINE_BINDINGS
            ),
            Counter({"pyposmat": 23, "vasp": 6, "lammps": 2}),
        )
        for binding in pypospack_bindings.ENGINE_BINDINGS:
            with self.subTest(engine=binding.engine_name):
                self.assertIs(
                    pypospack_bindings.engine_binding(binding.engine_name),
                    binding,
                )
                self.assertEqual(
                    pypospack_bindings.SOURCE_EXAMPLE_TREES[binding.example_root],
                    binding.example_tree,
                )

    def test__engine_binding__rejects_unknown_engine_name(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown PyPosPack"):
            pypospack_bindings.engine_binding("pypospack-unknown")


if __name__ == "__main__":
    unittest.main()
