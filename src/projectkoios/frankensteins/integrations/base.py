"""Nominal execution boundary for external-application integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class BaseExecutor[RequestT, ResultT](ABC):
    """Require a typed request and explicit workspace from each executor."""

    @property
    @abstractmethod
    def application_name(self) -> str:
        """Return the stable external-application identifier."""

    @abstractmethod
    def execute(self, request: RequestT, *, workspace: Path) -> ResultT:
        """Execute one request in an explicit integration-owned workspace."""
