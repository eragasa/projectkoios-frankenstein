"""Composition boundary for ``data-file-schema.xml``."""

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
class QeDataFileSchemaXmlFile(QeOutputFile):
    """Declare one ``data-file-schema.xml`` file."""

    @classmethod
    def from_save_directory(cls, save_directory: str) -> QeDataFileSchemaXmlFile:
        """Construct the XML declaration beneath one QE save directory."""
        return cls(relative_path=cls._join(save_directory, "data-file-schema.xml"))


@final
@dataclass(frozen=True, slots=True)
class QeDataFileSchemaXmlFileResult(QeOutputFileResult[QeDataFileSchemaXmlFile]):
    """Reserve the result type for version-aware schema XML parsing."""

    def __post_init__(self) -> None:
        super(QeDataFileSchemaXmlFileResult, self).__post_init__()
        if type(self.output_file) is not QeDataFileSchemaXmlFile:
            raise TypeError("output_file must be a QeDataFileSchemaXmlFile")


@final
@dataclass(frozen=True, slots=True)
class QeDataFileSchemaXmlFileParser(QeOutputFileParser[QeDataFileSchemaXmlFile]):
    """Reserve parsing of ``data-file-schema.xml``."""

    def parse(
        self,
        payload: bytes,
        *,
        output_file: QeDataFileSchemaXmlFile,
    ) -> QeDataFileSchemaXmlFileResult:
        """Reject use until the versioned XML contract is implemented."""
        if type(output_file) is not QeDataFileSchemaXmlFile:
            raise TypeError("output_file must be a QeDataFileSchemaXmlFile")
        del payload
        # TODO(Project Koios): Implement version-aware QE schema XML parsing.
        raise NotImplementedError("data-file-schema.xml parsing is not implemented")
