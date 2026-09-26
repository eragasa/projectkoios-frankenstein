from __future__ import annotations

import unittest

from projectkoios.frankensteins.engines.pyflamestk_examples import (
    bindings as pyflamestk_bindings,
)


class PyflamestkExampleEngineBindingsTest(unittest.TestCase):
    def test__ENGINE_BINDINGS__catalog_every_source_example(self) -> None:
        self.assertEqual(len(pyflamestk_bindings.ENGINE_BINDINGS), 17)
        self.assertEqual(len(pyflamestk_bindings.SOURCE_EXAMPLE_TREES), 17)
        self.assertEqual(
            sum(
                binding.status == "reconstructable"
                for binding in pyflamestk_bindings.ENGINE_BINDINGS
            ),
            16,
        )
        self.assertEqual(
            sum(
                binding.status == "blocked"
                for binding in pyflamestk_bindings.ENGINE_BINDINGS
            ),
            1,
        )
        self.assertEqual(
            len(
                {
                    binding.example_tree
                    for binding in pyflamestk_bindings.ENGINE_BINDINGS
                }
            ),
            15,
        )
        self.assertEqual(
            sum(
                binding.content_alias_of is not None
                for binding in pyflamestk_bindings.ENGINE_BINDINGS
            ),
            2,
        )
        for binding in pyflamestk_bindings.ENGINE_BINDINGS:
            with self.subTest(engine=binding.engine_name):
                self.assertIs(
                    pyflamestk_bindings.engine_binding(binding.engine_name),
                    binding,
                )
                self.assertEqual(
                    pyflamestk_bindings.SOURCE_EXAMPLE_TREES[binding.example_root],
                    binding.example_tree,
                )

    def test__engine_binding__rejects_unknown_engine_name(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown PyFlamestk"):
            pyflamestk_bindings.engine_binding("pyflamestk-unknown")


if __name__ == "__main__":
    unittest.main()
