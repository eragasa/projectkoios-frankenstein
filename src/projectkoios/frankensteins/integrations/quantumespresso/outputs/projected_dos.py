"""Composition boundary for ``projwfc.x`` output files."""

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
class QeProjectedDosFile(QeOutputFile):
    """Declare the ``filproj`` output selected for ``projwfc.x``."""


@final
@dataclass(frozen=True, slots=True)
class QeProjectedDosFileResult(QeOutputFileResult[QeProjectedDosFile]):
    """Reserve the result type for projected-DOS parsing."""

    def __post_init__(self) -> None:
        super(QeProjectedDosFileResult, self).__post_init__()
        if type(self.output_file) is not QeProjectedDosFile:
            raise TypeError("output_file must be a QeProjectedDosFile")


@final
@dataclass(frozen=True, slots=True)
class QeProjectedDosFileParser(QeOutputFileParser[QeProjectedDosFile]):
    """Reserve parsing of ``projwfc.x`` projected-DOS output."""

    def parse(
        self,
        payload: bytes,
        *,
        output_file: QeProjectedDosFile,
    ) -> QeProjectedDosFileResult:
        """Reject use until the ``filproj`` format contract is specified."""
        if type(output_file) is not QeProjectedDosFile:
            raise TypeError("output_file must be a QeProjectedDosFile")
        del payload
        # TODO(Project Koios): Implement declared projwfc.x output parsing.
        raise NotImplementedError("projwfc.x output parsing is not implemented")
