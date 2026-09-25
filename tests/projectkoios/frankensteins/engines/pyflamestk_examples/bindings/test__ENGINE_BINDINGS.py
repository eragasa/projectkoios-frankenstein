from __future__ import annotations

import unittest

from projectkoios.frankensteins.engines.pyflamestk_examples import (
    ENGINE_BINDINGS,
    SOURCE_EXAMPLE_TREES,
    engine_binding,
)


class PyflamestkExampleEngineBindingsTest(unittest.TestCase):
    def test_catalogs_every_engine_shaped_source_example(self) -> None:
        self.assertEqual(len(ENGINE_BINDINGS), 17)
        self.assertEqual(len(SOURCE_EXAMPLE_TREES), 17)
        self.assertEqual(
            sum(binding.status == "reconstructable" for binding in ENGINE_BINDINGS),
            16,
        )
        self.assertEqual(
            sum(binding.status == "blocked" for binding in ENGINE_BINDINGS),
            1,
        )
        self.assertEqual(len({binding.example_tree for binding in ENGINE_BINDINGS}), 15)
        self.assertEqual(
            sum(binding.content_alias_of is not None for binding in ENGINE_BINDINGS),
            2,
        )
        for binding in ENGINE_BINDINGS:
            with self.subTest(engine=binding.engine_name):
                self.assertIs(engine_binding(binding.engine_name), binding)
                self.assertEqual(
                    SOURCE_EXAMPLE_TREES[binding.example_root],
                    binding.example_tree,
                )

    def test_rejects_an_unknown_engine_name(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown PyFlamestk"):
            engine_binding("pyflamestk-unknown")


if __name__ == "__main__":
    unittest.main()
