from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from projectkoios.frankensteins.core import ObservedSetting, SourceFileEvidence
from projectkoios.frankensteins.integrations.lammps.models import (
    LammpsCommandIntent,
    LammpsIntegrationObservation,
    LammpsTemplateObservation,
)

_COMMAND = re.compile(
    r"(?:\$\{LAMMPS_BIN\}|\$LAMMPS_BIN)\s+-i\s+([^\s>]+)\s*>\s*([^\s]+)"
)


def inspect_lammps_templates(
    *,
    simulation_settings: Sequence[ObservedSetting],
    evidence_by_path: Mapping[str, SourceFileEvidence],
    text_by_path: Mapping[str, str],
) -> LammpsIntegrationObservation:
    templates: list[LammpsTemplateObservation] = []
    for setting in simulation_settings:
        if setting.key != "lmps_sim_type" or len(setting.values) != 2:
            raise ValueError("LAMMPS simulation setting must have name and directory")
        simulation_name, directory_name = setting.values
        template_directory = f"lmp_scripts_db/{directory_name}"
        prefix = template_directory + "/"
        files = tuple(
            sorted(
                (
                    evidence
                    for path, evidence in evidence_by_path.items()
                    if path.startswith(prefix)
                ),
                key=lambda item: item.relative_path,
            )
        )
        if not files:
            raise ValueError(f"LAMMPS template is missing: {template_directory}")
        runner_path = prefix + "runsimulation.sh"
        runner = evidence_by_path.get(runner_path)
        runner_text = text_by_path.get(runner_path)
        if runner is None or runner_text is None:
            raise ValueError(f"LAMMPS runner is missing: {runner_path}")
        matches = [
            match
            for line in runner_text.splitlines()
            if (match := _COMMAND.search(line)) is not None
        ]
        if len(matches) != 1:
            raise ValueError(f"LAMMPS runner command is ambiguous: {runner_path}")
        input_name, stdout_name = matches[0].groups()
        input_path = prefix + input_name
        if input_path not in evidence_by_path:
            raise ValueError(f"LAMMPS input script is missing: {input_path}")
        intent = LammpsCommandIntent(
            simulation_name=simulation_name,
            executable_environment_variable="LAMMPS_BIN",
            input_script=input_name,
            stdout_artifact=stdout_name,
            runner_script=runner,
        )
        templates.append(
            LammpsTemplateObservation(
                simulation_name=simulation_name,
                template_directory=template_directory,
                files=files,
                command_intent=intent,
            )
        )
    return LammpsIntegrationObservation(templates=tuple(templates))
