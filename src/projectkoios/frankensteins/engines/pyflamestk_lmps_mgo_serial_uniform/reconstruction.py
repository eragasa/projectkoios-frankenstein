from __future__ import annotations

import ast
import hashlib
from pathlib import Path

from projectkoios.frankensteins.core import (
    FrankensteinRecipe,
    IntegrationObservation,
    ObservedSetting,
    RecipeWarning,
    SourceFileEvidence,
)
from projectkoios.frankensteins.evidence import read_bounded_regular_file
from projectkoios.frankensteins.integrations.lammps import (
    inspect_lammps_templates,
)
from projectkoios.frankensteins.integrations.vasp import inspect_poscar

from .constants import (
    ENGINE_NAME,
    EXAMPLE_ROOT,
    SOURCE_COMPONENT,
    SOURCE_FILES,
    SOURCE_LICENSE_PATH,
    SOURCE_LICENSE_SHA256,
    SOURCE_REPOSITORY_URL,
    SOURCE_REVISION,
    SOURCE_TREE,
)
from .mathematical_models import reconstruct_mathematical_models

_MAX_FILE_BYTES = 10_000_000
_MACHINE_KEYS = {"lmps_bin", "lmps_exe_script"}


def reconstruct_checkout(checkout_root: Path) -> FrankensteinRecipe:
    """Reconstruct the bound engine from an explicit PyFlamestk checkout."""
    license_payload = read_bounded_regular_file(
        checkout_root,
        SOURCE_LICENSE_PATH,
        maximum_bytes=_MAX_FILE_BYTES,
        label="PyFlamestk source license",
    )
    if hashlib.sha256(license_payload).hexdigest() != SOURCE_LICENSE_SHA256:
        raise ValueError("PyFlamestk source license does not match its bound hash")

    prefix = EXAMPLE_ROOT + "/"
    selected_files = {
        path[len(prefix) :]: identity
        for path, identity in SOURCE_FILES.items()
        if path.startswith(prefix)
    }
    files = tuple(sorted(selected_files))

    evidence: list[SourceFileEvidence] = []
    text_by_path: dict[str, str] = {}
    for relative_path in files:
        payload = read_bounded_regular_file(
            checkout_root,
            f"{EXAMPLE_ROOT}/{relative_path}",
            maximum_bytes=_MAX_FILE_BYTES,
            label=f"PyFlamestk example file {relative_path}",
        )
        digest = hashlib.sha256(payload).hexdigest()
        expected_digest, expected_size = selected_files[relative_path]
        if digest != expected_digest or len(payload) != expected_size:
            raise ValueError(f"PyFlamestk example identity mismatch: {relative_path}")
        evidence.append(
            SourceFileEvidence(
                relative_path=relative_path,
                sha256=digest,
                byte_size=len(payload),
            )
        )
        try:
            text_by_path[relative_path] = payload.decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            raise ValueError(
                f"PyFlamestk example is not UTF-8 text: {relative_path}"
            ) from error
    evidence_by_path = {item.relative_path: item for item in evidence}
    settings = _settings(text_by_path)
    simulation_settings = tuple(
        setting for setting in settings if setting.key == "lmps_sim_type"
    )
    lammps = inspect_lammps_templates(
        simulation_settings=simulation_settings,
        evidence_by_path=evidence_by_path,
        text_by_path=text_by_path,
    )

    structure_settings = tuple(
        setting for setting in settings if setting.key == "structure"
    )
    structures = []
    for setting in structure_settings:
        if len(setting.values) != 3:
            raise ValueError("structure setting must have name, file, and format")
        name, filename, file_type = setting.values
        if file_type.casefold() != "vasp":
            raise ValueError("only explicitly declared VASP structures are supported")
        relative_path = f"structure_db/{filename}"
        file_evidence = evidence_by_path.get(relative_path)
        text = text_by_path.get(relative_path)
        if file_evidence is None or text is None:
            raise ValueError(f"VASP structure evidence is missing: {relative_path}")
        structures.append(inspect_poscar(name=name, evidence=file_evidence, text=text))

    integrations = (
        IntegrationObservation.from_payload(
            integration="integrations.lammps",
            contract_version="0.1.0",
            payload=lammps.to_dict(),
        ),
        IntegrationObservation.from_payload(
            integration="integrations.vasp",
            contract_version="0.1.0",
            payload={
                "format": "POSCAR",
                "structures": [item.to_dict() for item in structures],
                "external_execution_authorized": False,
                "pseudopotential_selection_authorized": False,
                "scientific_validation_claimed": False,
            },
        ),
    )

    mathematical_models = reconstruct_mathematical_models(checkout_root)
    warnings = _warnings(text_by_path)
    return FrankensteinRecipe(
        engine_name=ENGINE_NAME,
        source_component=SOURCE_COMPONENT,
        source_repository_url=SOURCE_REPOSITORY_URL,
        source_revision=SOURCE_REVISION,
        source_tree=SOURCE_TREE,
        source_example_root=EXAMPLE_ROOT,
        source_license_path=SOURCE_LICENSE_PATH,
        source_license_sha256=SOURCE_LICENSE_SHA256,
        source_files=tuple(evidence),
        settings=settings,
        integrations=integrations,
        mathematical_models=mathematical_models,
        warnings=warnings,
    )


def _settings(text_by_path: dict[str, str]) -> tuple[ObservedSetting, ...]:
    records: list[ObservedSetting] = []
    for relative_path in ("pyposmat.config", "pyposmat.potential", "pyposmat.qoi"):
        text = text_by_path[relative_path]
        for line_number, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                raise ValueError(f"invalid setting at {relative_path}:{line_number}")
            key, raw_value = (part.strip() for part in stripped.split("=", 1))
            if key in _MACHINE_KEYS:
                continue
            values = tuple(
                part.strip() for part in raw_value.split(",") if part.strip()
            )
            records.append(
                ObservedSetting(
                    key=key,
                    values=values,
                    evidence_path=relative_path,
                    line_number=line_number,
                )
            )
    records.extend(_python_settings(text_by_path["buckingham_uniform.py"]))
    return tuple(records)


def _python_settings(text: str) -> tuple[ObservedSetting, ...]:
    tree = ast.parse(text, filename="buckingham_uniform.py", mode="exec")
    selected: dict[str, tuple[str, int]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        key: str | None = None
        if isinstance(target, ast.Name) and target.id in {
            "n_simulations",
            "n_seed",
            "is_restart",
        }:
            key = target.id
        elif (
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == "mc_sampler"
            and target.attr == "sampler_type"
        ):
            key = "sampler_type"
        if key is None:
            continue
        value = ast.literal_eval(node.value)
        if value is None:
            rendered = "null"
        elif isinstance(value, bool):
            rendered = str(value).casefold()
        elif isinstance(value, (str, int, float)):
            rendered = str(value)
        else:
            raise ValueError(f"unsupported historical Python setting: {key}")
        selected[key] = (rendered, node.lineno)
    required = {"n_simulations", "n_seed", "is_restart", "sampler_type"}
    if set(selected) != required:
        raise ValueError("historical Python sampling settings are incomplete")
    return tuple(
        ObservedSetting(
            key=key,
            values=(selected[key][0],),
            evidence_path="buckingham_uniform.py",
            line_number=selected[key][1],
        )
        for key in sorted(selected)
    )


def _warnings(text_by_path: dict[str, str]) -> tuple[RecipeWarning, ...]:
    runner_paths = tuple(
        sorted(path for path in text_by_path if path.endswith("/runsimulation.sh"))
    )
    warnings = [
        RecipeWarning(
            code="external_execution_protected",
            evidence_paths=runner_paths,
            detail=(
                "Historical runner scripts describe LAMMPS execution, but this "
                "recipe records command intents only and grants no execution authority."
            ),
        ),
        RecipeWarning(
            code="machine_specific_executable_ignored",
            evidence_paths=("pyposmat.config", *runner_paths),
            detail=(
                "Historical absolute executable locations and hostname branches are "
                "not carried into the reconstructed command boundary."
            ),
        ),
        RecipeWarning(
            code="restart_behavior_observed",
            evidence_paths=("buckingham_uniform.py",),
            detail=(
                "The historical script requests restart behavior; the reconstruction "
                "records this setting but does not infer compatible restart artifacts."
            ),
        ),
    ]
    readme = text_by_path["README"]
    referenced_python = {
        token.strip("`>'\"")
        for token in readme.split()
        if token.strip("`>'\"").endswith(".py")
    }
    absent = sorted(path for path in referenced_python if path not in text_by_path)
    if absent:
        warnings.append(
            RecipeWarning(
                code="historical_readme_entrypoint_mismatch",
                evidence_paths=("README", "buckingham_uniform.py"),
                detail=(
                    "The historical README names an entry point that is absent from "
                    "the retained example; the present script is not silently renamed."
                ),
            )
        )
    return tuple(warnings)
