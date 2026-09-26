"""Composition boundary for ``pp.x`` ``plot_num`` output files."""

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
class QePlotNumFile(QeOutputFile):
    """Declare one volumetric ``plot_num`` output produced by ``pp.x``."""


@final
@dataclass(frozen=True, slots=True)
class QePlotNumFileResult(QeOutputFileResult[QePlotNumFile]):
    """Reserve the result type for ``plot_num`` parsing."""

    def __post_init__(self) -> None:
        super(QePlotNumFileResult, self).__post_init__()
        if type(self.output_file) is not QePlotNumFile:
            raise TypeError("output_file must be a QePlotNumFile")


@final
@dataclass(frozen=True, slots=True)
class QePlotNumFileParser(QeOutputFileParser[QePlotNumFile]):
    """Reserve parsing of ``pp.x`` volumetric output."""

    def parse(
        self,
        payload: bytes,
        *,
        output_file: QePlotNumFile,
    ) -> QePlotNumFileResult:
        """Reject use until the selected output format is specified."""
        if type(output_file) is not QePlotNumFile:
            raise TypeError("output_file must be a QePlotNumFile")
        del payload
        # TODO(Project Koios): Implement format-specific pp.x volumetric parsing.
        raise NotImplementedError("pp.x plot_num output parsing is not implemented")
