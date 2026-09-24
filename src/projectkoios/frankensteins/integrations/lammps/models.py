from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from projectkoios.frankensteins.core import SourceFileEvidence


def _relative(value: str) -> None:
    path = PurePosixPath(value)
    if (
        not value
        or value != path.as_posix()
        or path.is_absolute()
        or "." in path.parts
        or ".." in path.parts
    ):
        raise ValueError("LAMMPS path must be normalized and relative")


@dataclass(frozen=True)
class LammpsCommandIntent:
    simulation_name: str
    executable_environment_variable: str
    input_script: str
    stdout_artifact: str
    runner_script: SourceFileEvidence
    execution_authorized: bool = False

    def __post_init__(self) -> None:
        if not self.simulation_name or len(self.simulation_name) > 128:
            raise ValueError("simulation name is invalid")
        if self.executable_environment_variable != "LAMMPS_BIN":
            raise ValueError("only the explicit LAMMPS_BIN boundary is supported")
        _relative(self.input_script)
        _relative(self.stdout_artifact)
        if self.execution_authorized:
            raise ValueError("a LAMMPS command intent cannot authorize execution")

    def to_dict(self) -> dict[str, object]:
        return {
            "simulation_name": self.simulation_name,
            "program": "lammps",
            "executable_environment_variable": self.executable_environment_variable,
            "arguments": ["-i", self.input_script],
            "stdout_artifact": self.stdout_artifact,
            "runner_script": self.runner_script.to_dict(),
            "execution_authorized": self.execution_authorized,
        }


@dataclass(frozen=True)
class LammpsTemplateObservation:
    simulation_name: str
    template_directory: str
    files: tuple[SourceFileEvidence, ...]
    command_intent: LammpsCommandIntent

    def __post_init__(self) -> None:
        _relative(self.template_directory)
        if not self.files:
            raise ValueError("LAMMPS template must retain file evidence")
        paths = tuple(item.relative_path for item in self.files)
        if paths != tuple(sorted(paths)) or len(paths) != len(set(paths)):
            raise ValueError("LAMMPS template files must have unique sorted paths")

    def to_dict(self) -> dict[str, object]:
        return {
            "simulation_name": self.simulation_name,
            "template_directory": self.template_directory,
            "files": [item.to_dict() for item in self.files],
            "command_intent": self.command_intent.to_dict(),
        }


@dataclass(frozen=True)
class LammpsIntegrationObservation:
    templates: tuple[LammpsTemplateObservation, ...]
    external_execution_authorized: bool = False

    def __post_init__(self) -> None:
        if not self.templates:
            raise ValueError("LAMMPS integration requires templates")
        names = tuple(item.simulation_name for item in self.templates)
        if len(names) != len(set(names)):
            raise ValueError("LAMMPS simulation names must be unique")
        if self.external_execution_authorized:
            raise ValueError("LAMMPS integration cannot authorize execution")

    def to_dict(self) -> dict[str, object]:
        return {
            "calculator": "lammps",
            "templates": [item.to_dict() for item in self.templates],
            "external_execution_authorized": self.external_execution_authorized,
            "numerical_verification_claimed": False,
            "scientific_validation_claimed": False,
        }
