"""Composition boundary for ``prefix.rho`` output files."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from projectkoios.frankensteins.integrations.quantumespresso.outputs.base import (
    QeOutputFile,
    QeOutputFileParser,
    QeOutputFileResult,
)


@final
@dataclass(frozen=True, slots=True)
class QeChargeDensityFile(QeOutputFile):
    """Declare one ``prefix.rho`` charge-density file."""

    @classmethod
    def from_prefix(
        cls,
        *,
        prefix: str,
        directory: str = "",
    ) -> QeChargeDensityFile:
        """Construct one charge-density-file declaration."""
        cls._validate_prefix(prefix)
        return cls(relative_path=cls._join(directory, f"{prefix}.rho"))


@final
@dataclass(frozen=True, slots=True)
class QeChargeDensityFileResult(QeOutputFileResult[QeChargeDensityFile]):
    """Reserve the result type for charge-density parsing."""

    def __post_init__(self) -> None:
        super(QeChargeDensityFileResult, self).__post_init__()
        if type(self.output_file) is not QeChargeDensityFile:
            raise TypeError("output_file must be a QeChargeDensityFile")


@final
@dataclass(frozen=True, slots=True)
class QeChargeDensityFileParser(QeOutputFileParser[QeChargeDensityFile]):
    """Reserve parsing of ``prefix.rho`` files."""

    def parse(
        self,
        payload: bytes,
        *,
        output_file: QeChargeDensityFile,
    ) -> QeChargeDensityFileResult:
        """Reject use until supported charge-density formats are specified."""
        if type(output_file) is not QeChargeDensityFile:
            raise TypeError("output_file must be a QeChargeDensityFile")
        del payload
        # TODO(Project Koios): Implement version-aware charge-density parsing.
        raise NotImplementedError("charge-density-file parsing is not implemented")
