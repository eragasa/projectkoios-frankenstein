"""NumPy adapter for continuous uniform random sampling."""

from __future__ import annotations

import math

import numpy as np

from projectkoios.frankensteins.adapters.base import Binding


class NumpyAdapter(Binding):
    """Adapt uniform random sampling to an isolated NumPy random state."""

    __slots__ = ()

    def sample_uniform(
        self,
        lower_bound: float,
        upper_bound: float,
        sample_count: int,
        /,
        *,
        random_seed: int | None,
    ) -> tuple[float, ...]:
        """Return closed-open uniform samples without mutating global state."""

        if not math.isfinite(lower_bound) or not math.isfinite(upper_bound):
            raise ValueError("uniform bounds must be finite")
        if lower_bound >= upper_bound:
            raise ValueError("lower_bound must be less than upper_bound")
        if not isinstance(sample_count, int) or isinstance(sample_count, bool):
            raise ValueError("sample_count must be an integer")
        if sample_count <= 0:
            raise ValueError("sample_count must be positive")
        if random_seed is not None and (
            not isinstance(random_seed, int) or isinstance(random_seed, bool)
        ):
            raise ValueError("random_seed must be an integer or None")

        try:
            random_state = np.random.RandomState(random_seed)
        except ValueError as error:
            raise ValueError("random_seed is outside NumPy's valid range") from error

        samples = random_state.uniform(
            low=lower_bound,
            high=upper_bound,
            size=sample_count,
        )
        return tuple(float(value) for value in samples)

    def sample_independent_uniform(
        self,
        bounds: tuple[tuple[float, float], ...],
        sample_count: int,
        /,
        *,
        random_seed: int | None,
    ) -> tuple[tuple[float, ...], ...]:
        """Return row-major samples from independent uniform dimensions."""

        if not isinstance(bounds, tuple) or not bounds:
            raise ValueError("bounds must be a non-empty tuple")
        for dimension, bound in enumerate(bounds):
            if not isinstance(bound, tuple) or len(bound) != 2:
                raise ValueError(
                    f"bounds[{dimension}] must contain lower and upper bounds"
                )
            lower_bound, upper_bound = bound
            if isinstance(lower_bound, bool) or isinstance(upper_bound, bool):
                raise ValueError("uniform bounds must be finite numbers")
            if not math.isfinite(lower_bound) or not math.isfinite(upper_bound):
                raise ValueError("uniform bounds must be finite")
            if lower_bound >= upper_bound:
                raise ValueError("lower_bound must be less than upper_bound")
        if not isinstance(sample_count, int) or isinstance(sample_count, bool):
            raise ValueError("sample_count must be an integer")
        if sample_count <= 0:
            raise ValueError("sample_count must be positive")
        if random_seed is not None and (
            not isinstance(random_seed, int) or isinstance(random_seed, bool)
        ):
            raise ValueError("random_seed must be an integer or None")

        try:
            random_state = np.random.RandomState(random_seed)
        except ValueError as error:
            raise ValueError("random_seed is outside NumPy's valid range") from error

        lower_bounds = np.asarray(
            tuple(lower_bound for lower_bound, _upper_bound in bounds),
            dtype=np.float64,
        )
        upper_bounds = np.asarray(
            tuple(upper_bound for _lower_bound, upper_bound in bounds),
            dtype=np.float64,
        )
        samples = random_state.uniform(
            low=lower_bounds,
            high=upper_bounds,
            size=(sample_count, len(bounds)),
        )
        return tuple(tuple(float(value) for value in sample) for sample in samples)


__all__ = ["NumpyAdapter"]
