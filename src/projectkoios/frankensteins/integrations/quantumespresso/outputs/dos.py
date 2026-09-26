"""Composition boundary for ``dos.x`` output files."""

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
class QeDosFile(QeOutputFile):
    """Declare the ``fildos`` output selected for ``dos.x``."""


@final
@dataclass(frozen=True, slots=True)
class QeDosFileResult(QeOutputFileResult[QeDosFile]):
    """Reserve the result type for DOS parsing."""

    def __post_init__(self) -> None:
        super(QeDosFileResult, self).__post_init__()
        if type(self.output_file) is not QeDosFile:
            raise TypeError("output_file must be a QeDosFile")


@final
@dataclass(frozen=True, slots=True)
class QeDosFileParser(QeOutputFileParser[QeDosFile]):
    """Reserve parsing of ``dos.x`` output."""

    def parse(
        self,
        payload: bytes,
        *,
        output_file: QeDosFile,
    ) -> QeDosFileResult:
        """Reject use until the ``fildos`` format contract is specified."""
        if type(output_file) is not QeDosFile:
            raise TypeError("output_file must be a QeDosFile")
        del payload
        # TODO(Project Koios): Implement declared dos.x output parsing.
        raise NotImplementedError("dos.x output parsing is not implemented")
