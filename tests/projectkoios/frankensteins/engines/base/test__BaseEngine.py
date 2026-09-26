from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from projectkoios.frankensteins.engines import base as engine_base
from projectkoios.frankensteins.engines.pyflamestk_examples import (
    bindings as pyflamestk_bindings,
)
from projectkoios.frankensteins.engines.pypospack_examples import (
    bindings as pypospack_bindings,
)


class BaseEngineTest(unittest.TestCase):
    def test__BaseEngine__is_common_nominal_base(self) -> None:
        engines = (
            *pyflamestk_bindings.ENGINE_BINDINGS,
            *pypospack_bindings.ENGINE_BINDINGS,
        )

        self.assertEqual(len(engines), 48)
        self.assertTrue(
            all(isinstance(engine, engine_base.BaseEngine) for engine in engines)
        )

    def test__BaseEngine__is_immutable_slotted_metadata(self) -> None:
        engine = engine_base.BaseEngine(
            engine_name="example-engine",
            example_root="examples/example",
            example_tree="0" * 40,
            entrypoints=("run.py",),
        )

        with self.assertRaises(FrozenInstanceError):
            engine.engine_name = "changed"  # type: ignore[misc]
        self.assertFalse(hasattr(engine, "__dict__"))
        self.assertFalse(hasattr(engine, "run"))
        self.assertFalse(hasattr(engine, "evaluate"))

    def test__BaseEngine__rejects_invalid_identity_fields(self) -> None:
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
                engine_base.BaseEngine(
                    **{**valid, field_name: value}  # type: ignore[arg-type]
                )


if __name__ == "__main__":
    unittest.main()
