"""Composed probability distributions, parameters, and sampler behavior."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

import numpy as np

from projectkoios.frankensteins.adapters.base import Binding
from projectkoios.frankensteins.adapters.bindings.numpy.probability import (
    NumpyAdapter,
)
from projectkoios.frankensteins.validation.base import (
    ValidationRequest,
    ValidationResult,
    Validator,
)


class ProbabilityError(ValueError):
    """A probability distribution, sampler, or sampling request is invalid."""


@dataclass(frozen=True, slots=True)
class ProbabilityDistributionParameters:
    """Nominal base for immutable probability-distribution parameters."""


@dataclass(frozen=True, slots=True)
class UniformProbabilityDistributionParameters(ProbabilityDistributionParameters):
    """Finite bounds of a closed-open continuous uniform distribution."""

    lower_bound: float
    upper_bound: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.lower_bound):
            raise ProbabilityError("lower_bound must be finite")
        if not math.isfinite(self.upper_bound):
            raise ProbabilityError("upper_bound must be finite")
        if self.lower_bound >= self.upper_bound:
            raise ProbabilityError("lower_bound must be less than upper_bound")


class ProbabilityDistributionSamplerAdapter(StrEnum):
    """Stable configuration names for supported sampler adapters."""

    NUMPY = "numpy"


@dataclass(frozen=True, slots=True)
class ProbabilityDistributionSampler[
    ParametersT: ProbabilityDistributionParameters,
    AdapterT: Binding,
](ABC):
    """Sampler behavior composed from distribution parameters and an adapter."""

    parameters: ParametersT
    adapter: AdapterT

    supported_adapters: ClassVar[tuple[type[Binding], ...]] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.parameters, ProbabilityDistributionParameters):
            raise ProbabilityError(
                "parameters must be ProbabilityDistributionParameters"
            )
        if not isinstance(self.adapter, self.supported_adapters):
            raise ProbabilityError(
                f"unsupported probability-distribution adapter: "
                f"{type(self.adapter).__name__}"
            )

    @abstractmethod
    def sample(
        self,
        sample_count: int,
        /,
        *,
        random_seed: int | None,
    ) -> tuple[float, ...]:
        """Return samples by delegating to the composed adapter."""


@dataclass(frozen=True, slots=True)
class UniformProbabilityDistributionSampler(
    ProbabilityDistributionSampler[
        UniformProbabilityDistributionParameters,
        NumpyAdapter,
    ]
):
    """Uniform sampler behavior supported by the NumPy adapter."""

    supported_adapters: ClassVar[tuple[type[Binding], ...]] = (NumpyAdapter,)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.parameters, UniformProbabilityDistributionParameters):
            raise ProbabilityError(
                "parameters must be UniformProbabilityDistributionParameters"
            )

    def sample(
        self,
        sample_count: int,
        /,
        *,
        random_seed: int | None,
    ) -> tuple[float, ...]:
        """Return uniform samples through the composed NumPy adapter."""

        try:
            return self.adapter.sample_uniform(
                self.parameters.lower_bound,
                self.parameters.upper_bound,
                sample_count,
                random_seed=random_seed,
            )
        except ValueError as error:
            raise ProbabilityError(str(error)) from error


@dataclass(frozen=True, slots=True)
class UniformProbabilityDistributionSamplerValidationRequest(ValidationRequest):
    """Immutable replayable request for uniform-sampler validation."""

    sampler: UniformProbabilityDistributionSampler
    sample_count: int
    random_seed: int
    bin_count: int = 20
    standard_error_limit: float = 6.0

    def __post_init__(self) -> None:
        if not isinstance(self.sampler, UniformProbabilityDistributionSampler):
            raise ProbabilityError(
                "sampler must be a UniformProbabilityDistributionSampler"
            )
        for field_name, value in (
            ("sample_count", self.sample_count),
            ("random_seed", self.random_seed),
            ("bin_count", self.bin_count),
        ):
            if not isinstance(value, int) or isinstance(value, bool):
                raise ProbabilityError(f"{field_name} must be an integer")
        if self.sample_count <= 0:
            raise ProbabilityError("sample_count must be positive")
        if self.bin_count <= 1:
            raise ProbabilityError("bin_count must be greater than one")
        if not math.isfinite(self.standard_error_limit):
            raise ProbabilityError("standard_error_limit must be finite")
        if self.standard_error_limit <= 0.0:
            raise ProbabilityError("standard_error_limit must be positive")


@dataclass(frozen=True, slots=True)
class UniformProbabilityDistributionSamplerValidation(ValidationResult):
    """Immutable statistical validation result for one uniform sampler run."""

    sample_count: int
    support_is_valid: bool
    mean_absolute_error: float
    mean_acceptance_limit: float
    variance_absolute_error: float
    variance_acceptance_limit: float
    maximum_bin_count_deviation: float
    bin_count_acceptance_limit: float

    def __post_init__(self) -> None:
        if not isinstance(self.sample_count, int) or isinstance(
            self.sample_count, bool
        ):
            raise ProbabilityError("sample_count must be an integer")
        if self.sample_count <= 0:
            raise ProbabilityError("sample_count must be positive")
        if type(self.support_is_valid) is not bool:
            raise ProbabilityError("support_is_valid must be a boolean")
        for field_name in (
            "mean_absolute_error",
            "mean_acceptance_limit",
            "variance_absolute_error",
            "variance_acceptance_limit",
            "maximum_bin_count_deviation",
            "bin_count_acceptance_limit",
        ):
            value = getattr(self, field_name)
            if not math.isfinite(value) or value < 0.0:
                raise ProbabilityError(f"{field_name} must be nonnegative and finite")
        for field_name in (
            "mean_acceptance_limit",
            "variance_acceptance_limit",
            "bin_count_acceptance_limit",
        ):
            if getattr(self, field_name) == 0.0:
                raise ProbabilityError(f"{field_name} must be positive")

    @property
    def is_valid(self) -> bool:
        """Return whether every statistical validation criterion passed."""

        return (
            self.support_is_valid
            and self.mean_absolute_error < self.mean_acceptance_limit
            and self.variance_absolute_error < self.variance_acceptance_limit
            and self.maximum_bin_count_deviation < self.bin_count_acceptance_limit
        )


class UniformProbabilityDistributionSamplerValidator(
    Validator[
        UniformProbabilityDistributionSamplerValidationRequest,
        UniformProbabilityDistributionSamplerValidation,
    ]
):
    """Run bounded statistical validation for a uniform sampler."""

    __slots__ = ()

    def validate(
        self,
        request: UniformProbabilityDistributionSamplerValidationRequest,
        /,
    ) -> UniformProbabilityDistributionSamplerValidation:
        """Sample and compare support, moments, and bin occupancy to theory."""

        if not isinstance(
            request,
            UniformProbabilityDistributionSamplerValidationRequest,
        ):
            raise ProbabilityError(
                "request must be a "
                "UniformProbabilityDistributionSamplerValidationRequest"
            )
        parameters = request.sampler.parameters
        samples = np.asarray(
            request.sampler.sample(
                request.sample_count,
                random_seed=request.random_seed,
            ),
            dtype=np.float64,
        )
        width = parameters.upper_bound - parameters.lower_bound
        expected_mean = (parameters.lower_bound + parameters.upper_bound) / 2.0
        expected_variance = width**2 / 12.0
        expected_fourth_central_moment = width**4 / 80.0
        mean_acceptance_limit = request.standard_error_limit * math.sqrt(
            expected_variance / request.sample_count
        )
        variance_acceptance_limit = request.standard_error_limit * math.sqrt(
            (expected_fourth_central_moment - expected_variance**2)
            / request.sample_count
        )
        bin_counts, _edges = np.histogram(
            samples,
            bins=request.bin_count,
            range=(parameters.lower_bound, parameters.upper_bound),
        )
        expected_bin_count = request.sample_count / request.bin_count
        bin_count_acceptance_limit = request.standard_error_limit * math.sqrt(
            expected_bin_count * (1.0 - 1.0 / request.bin_count)
        )

        return UniformProbabilityDistributionSamplerValidation(
            sample_count=request.sample_count,
            support_is_valid=(
                float(samples.min()) >= parameters.lower_bound
                and float(samples.max()) < parameters.upper_bound
            ),
            mean_absolute_error=abs(float(samples.mean()) - expected_mean),
            mean_acceptance_limit=mean_acceptance_limit,
            variance_absolute_error=abs(float(samples.var()) - expected_variance),
            variance_acceptance_limit=variance_acceptance_limit,
            maximum_bin_count_deviation=float(
                np.max(np.abs(bin_counts - expected_bin_count))
            ),
            bin_count_acceptance_limit=bin_count_acceptance_limit,
        )


@dataclass(frozen=True, slots=True)
class ProbabilityDistribution[
    ParametersT: ProbabilityDistributionParameters,
    AdapterT: Binding,
]:
    """Distribution composed from parameters and their configured sampler."""

    parameters: ParametersT
    sampler: ProbabilityDistributionSampler[ParametersT, AdapterT]

    def __post_init__(self) -> None:
        if not isinstance(self.parameters, ProbabilityDistributionParameters):
            raise ProbabilityError(
                "parameters must be ProbabilityDistributionParameters"
            )
        if not isinstance(self.sampler, ProbabilityDistributionSampler):
            raise ProbabilityError("sampler must be a ProbabilityDistributionSampler")
        if self.sampler.parameters is not self.parameters:
            raise ProbabilityError(
                "distribution and sampler must share the same parameters object"
            )


_SAMPLER_ADAPTER_TYPES: dict[
    ProbabilityDistributionSamplerAdapter,
    type[NumpyAdapter],
] = {
    ProbabilityDistributionSamplerAdapter.NUMPY: NumpyAdapter,
}


@dataclass(frozen=True, slots=True, init=False)
class UniformProbabilityDistribution(
    ProbabilityDistribution[
        UniformProbabilityDistributionParameters,
        NumpyAdapter,
    ]
):
    """Uniform distribution composed with its parameters and sampler."""

    def __init__(
        self,
        parameters: UniformProbabilityDistributionParameters,
        /,
        *,
        adapter: ProbabilityDistributionSamplerAdapter,
    ) -> None:
        if not isinstance(adapter, ProbabilityDistributionSamplerAdapter):
            raise ProbabilityError(
                "adapter must be a ProbabilityDistributionSamplerAdapter"
            )
        adapter_type = _SAMPLER_ADAPTER_TYPES[adapter]
        sampler = UniformProbabilityDistributionSampler(
            parameters=parameters,
            adapter=adapter_type(),
        )
        ProbabilityDistribution.__init__(
            self,
            parameters=parameters,
            sampler=sampler,
        )


__all__ = [
    "ProbabilityDistribution",
    "ProbabilityDistributionParameters",
    "ProbabilityDistributionSampler",
    "ProbabilityDistributionSamplerAdapter",
    "ProbabilityError",
    "UniformProbabilityDistribution",
    "UniformProbabilityDistributionParameters",
    "UniformProbabilityDistributionSampler",
    "UniformProbabilityDistributionSamplerValidation",
    "UniformProbabilityDistributionSamplerValidationRequest",
    "UniformProbabilityDistributionSamplerValidator",
]
