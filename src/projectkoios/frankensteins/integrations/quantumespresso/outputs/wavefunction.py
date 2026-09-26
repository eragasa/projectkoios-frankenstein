"""Composition boundary for ``prefix.wfc`` output files."""

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
class QeWavefunctionFile(QeOutputFile):
    """Declare one ``prefix.wfc`` or indexed ``prefix.wfc{N}`` file."""

    @classmethod
    def from_prefix(
        cls,
        *,
        prefix: str,
        directory: str = "",
        index: int | None = None,
    ) -> QeWavefunctionFile:
        """Construct one wavefunction-file declaration."""
        cls._validate_prefix(prefix)
        if index is not None and (type(index) is not int or index <= 0):
            raise ValueError("wavefunction index must be a positive integer")
        suffix = "" if index is None else str(index)
        return cls(relative_path=cls._join(directory, f"{prefix}.wfc{suffix}"))


@final
@dataclass(frozen=True, slots=True)
class QeWavefunctionFileResult(QeOutputFileResult[QeWavefunctionFile]):
    """Reserve the result type for wavefunction parsing."""

    def __post_init__(self) -> None:
        super(QeWavefunctionFileResult, self).__post_init__()
        if type(self.output_file) is not QeWavefunctionFile:
            raise TypeError("output_file must be a QeWavefunctionFile")


@final
@dataclass(frozen=True, slots=True)
class QeWavefunctionFileParser(QeOutputFileParser[QeWavefunctionFile]):
    """Reserve parsing of ``prefix.wfc`` files."""

    def parse(
        self,
        payload: bytes,
        *,
        output_file: QeWavefunctionFile,
    ) -> QeWavefunctionFileResult:
        """Reject use until supported wavefunction formats are specified."""
        if type(output_file) is not QeWavefunctionFile:
            raise TypeError("output_file must be a QeWavefunctionFile")
        del payload
        # TODO(Project Koios): Implement version- and build-aware WFC parsing.
        raise NotImplementedError("wavefunction-file parsing is not implemented")
