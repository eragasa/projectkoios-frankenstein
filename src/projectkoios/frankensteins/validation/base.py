"""Nominal request, result, and action bases for maintained validation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationRequest:
    """Nominal base for immutable validation inputs."""


@dataclass(frozen=True, slots=True)
class ValidationResult(ABC):
    """Nominal base for immutable validation evidence."""

    @property
    @abstractmethod
    def is_valid(self) -> bool:
        """Return whether the specialized validation criteria passed."""


class Validator[
    RequestT: ValidationRequest,
    ResultT: ValidationResult,
](ABC):
    """Runtime-enforced action from a validation request to its result."""

    @abstractmethod
    def validate(self, request: RequestT, /) -> ResultT:
        """Validate one immutable request and return immutable evidence."""


__all__ = ["ValidationRequest", "ValidationResult", "Validator"]
