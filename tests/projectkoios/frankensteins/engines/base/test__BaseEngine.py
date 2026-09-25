from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from projectkoios.frankensteins.engines import BaseEngine
from projectkoios.frankensteins.engines.pyflamestk_examples import (
    ENGINE_BINDINGS as PYFLAMESTK_ENGINES,
)
from projectkoios.frankensteins.engines.pypospack_examples import (
    ENGINE_BINDINGS as PYPOSPACK_ENGINES,
)


class BaseEngineTest(unittest.TestCase):
    def test_is_the_common_nominal_base_for_source_specific_bindings(self) -> None:
        engines = (*PYFLAMESTK_ENGINES, *PYPOSPACK_ENGINES)

        self.assertEqual(len(engines), 48)
        self.assertTrue(all(isinstance(engine, BaseEngine) for engine in engines))

    def test_is_immutable_metadata_and_has_no_execution_method(self) -> None:
        engine = BaseEngine(
            engine_name="example-engine",
            example_root="examples/example",
            example_tree="0" * 40,
            entrypoints=("run.py",),
        )

        with self.assertRaises(FrozenInstanceError):
            engine.engine_name = "changed"  # type: ignore[misc]
        self.assertFalse(hasattr(engine, "run"))
        self.assertFalse(hasattr(engine, "evaluate"))

    def test_rejects_invalid_common_identity_fields(self) -> None:
        valid = {
            "engine_name": "example-engine",
            "example_root": "examples/example",
            "example_tree": "0" * 40,
            "entrypoints": ("run.py",),
        }
        invalid_cases = (
            ("engine_name", "Example Engine", "engine_name"),
            ("example_root", "../example", "example_root"),
            ("example_tree", "not-a-tree", "example_tree"),
            ("entrypoints", (), "entrypoints"),
            ("entrypoints", ("nested/run.py",), "entrypoint"),
            ("entrypoints", ("run.py", "run.py"), "unique"),
        )
        for field_name, value, message in invalid_cases:
            with (
                self.subTest(field=field_name),
                self.assertRaisesRegex(
                    ValueError,
                    message,
                ),
            ):
                BaseEngine(**{**valid, field_name: value})  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
