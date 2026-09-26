"""Composition boundary for reviewed ``pw.x`` auxiliary output files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import final

from projectkoios.frankensteins.integrations.quantumespresso.outputs.base import (
    QeOutputFile,
    QeOutputFileParser,
    QeOutputFileResult,
)

_SUFFIX = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")


@final
@dataclass(frozen=True, slots=True)
class QePwAuxiliaryFile(QeOutputFile):
    """Declare one reviewed prefix-based auxiliary output file."""

    @classmethod
    def from_prefix(
        cls,
        *,
        prefix: str,
        suffix: str,
        directory: str = "",
    ) -> QePwAuxiliaryFile:
        """Construct one reviewed auxiliary-file declaration."""
        cls._validate_prefix(prefix)
        if type(suffix) is not str or not _SUFFIX.fullmatch(suffix):
            raise ValueError("auxiliary suffix must be a safe filename suffix")
        return cls(relative_path=cls._join(directory, f"{prefix}.{suffix}"))


@final
@dataclass(frozen=True, slots=True)
class QePwAuxiliaryFileResult(QeOutputFileResult[QePwAuxiliaryFile]):
    """Reserve the result type for prefix auxiliary parsing."""

    def __post_init__(self) -> None:
        super(QePwAuxiliaryFileResult, self).__post_init__()
        if type(self.output_file) is not QePwAuxiliaryFile:
            raise TypeError("output_file must be a QePwAuxiliaryFile")


@final
@dataclass(frozen=True, slots=True)
class QePwAuxiliaryFileParser(QeOutputFileParser[QePwAuxiliaryFile]):
    """Reserve parsing of reviewed prefix auxiliary files."""

    def parse(
        self,
        payload: bytes,
        *,
        output_file: QePwAuxiliaryFile,
    ) -> QePwAuxiliaryFileResult:
        """Reject use until each reviewed auxiliary schema is implemented."""
        if type(output_file) is not QePwAuxiliaryFile:
            raise TypeError("output_file must be a QePwAuxiliaryFile")
        del payload
        # TODO(Project Koios): Dispatch only across reviewed auxiliary schemas.
        raise NotImplementedError("pw.x auxiliary-file parsing is not implemented")
