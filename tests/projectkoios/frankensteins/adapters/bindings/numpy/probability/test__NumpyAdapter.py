from __future__ import annotations

import unittest

import numpy as np

from projectkoios.frankensteins.adapters.base import Adapter, Binding
from projectkoios.frankensteins.adapters.bindings.numpy.probability import NumpyAdapter


class NumpyAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = NumpyAdapter()

    def test_is_a_numpy_dependency_binding(self) -> None:
        self.assertIsInstance(self.adapter, Binding)
        self.assertIsInstance(self.adapter, Adapter)
        self.assertEqual(
            self.adapter.sample_uniform(1.5, 2.5, 4, random_seed=7),
            (
                1.5763082893739573,
                2.2799187922401147,
                1.9384092314408936,
                2.223465177830941,
            ),
        )

    def test_does_not_mutate_numpy_global_random_state(self) -> None:
        original_state = np.random.get_state()
        try:
            np.random.seed(19)
            expected = (float(np.random.uniform()), float(np.random.uniform()))
            np.random.seed(19)
            first = float(np.random.uniform())

            self.adapter.sample_uniform(1.5, 2.5, 2, random_seed=7)

            second = float(np.random.uniform())
            self.assertEqual((first, second), expected)
        finally:
            np.random.set_state(original_state)

    def test_rejects_invalid_requests(self) -> None:
        for sample_count in (0, -1, True):
            with (
                self.subTest(sample_count=sample_count),
                self.assertRaises(ValueError),
            ):
                self.adapter.sample_uniform(
                    1.5,
                    2.5,
                    sample_count,
                    random_seed=7,
                )

        with self.assertRaises(ValueError):
            self.adapter.sample_uniform(1.5, 2.5, 1, random_seed=-1)
        with self.assertRaises(ValueError):
            self.adapter.sample_uniform(
                1.5,
                2.5,
                1,
                random_seed=True,  # type: ignore[arg-type]
            )


if __name__ == "__main__":
    unittest.main()
