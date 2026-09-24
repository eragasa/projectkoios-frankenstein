from __future__ import annotations

import hashlib
import re
from pathlib import Path

from projectkoios.frankensteins.core import SourceFileEvidence
from projectkoios.frankensteins.evidence import read_bounded_regular_file
from projectkoios.frankensteins.mathematics.models import (
    ExternalMathematicalModelDeclaration,
    MathematicalModelCatalog,
    MathematicalModelDefinition,
    MathematicalModelInput,
    MathematicalModelKind,
    MathematicalModelSourceSpan,
)

from .constants import EXAMPLE_ROOT, SOURCE_COMPONENT, SOURCE_FILES, SOURCE_REVISION

_NEGATED_PARAMETER = re.compile(r"-([A-Za-z][A-Za-z0-9_]*)")
_QOI_IMPLEMENTATION_PATH = "pyflamestk/qoi.py"
_PARAMETER_IMPLEMENTATION_PATH = "pyflamestk/pyposmat.py"
_LAMMPS_IMPLEMENTATION_PATH = "pyflamestk/lammps.py"
_QOI_CONFIGURATION_PATH = f"{EXAMPLE_ROOT}/pyposmat.qoi"
_POTENTIAL_CONFIGURATION_PATH = f"{EXAMPLE_ROOT}/pyposmat.potential"
_MAX_SOURCE_BYTES = 2_000_000


def reconstruct_mathematical_models(
    checkout_root: Path,
) -> MathematicalModelCatalog:
    """Statically reconstruct pure scalar models from a bound checkout."""
    qoi_implementation, qoi_implementation_text = _verified_text(
        checkout_root,
        _QOI_IMPLEMENTATION_PATH,
    )
    parameter_implementation, parameter_implementation_text = _verified_text(
        checkout_root,
        _PARAMETER_IMPLEMENTATION_PATH,
    )
    lammps_implementation, lammps_implementation_text = _verified_text(
        checkout_root,
        _LAMMPS_IMPLEMENTATION_PATH,
    )
    qoi_configuration, qoi_configuration_text = _verified_text(
        checkout_root,
        _QOI_CONFIGURATION_PATH,
    )
    potential_configuration, potential_configuration_text = _verified_text(
        checkout_root,
        _POTENTIAL_CONFIGURATION_PATH,
    )

    _verify_implementation_spans(
        qoi_implementation_text=qoi_implementation_text,
        parameter_implementation_text=parameter_implementation_text,
        lammps_implementation_text=lammps_implementation_text,
    )

    models = [
        *_dependent_parameter_models(
            potential_configuration_text,
            potential_configuration,
            parameter_implementation,
        ),
        *_qoi_models(
            qoi_configuration_text,
            qoi_configuration,
            qoi_implementation,
        ),
    ]
    external_models = _external_potential_models(
        potential_configuration_text,
        potential_configuration,
        lammps_implementation,
    )
    return MathematicalModelCatalog(
        source_component=SOURCE_COMPONENT,
        source_revision=SOURCE_REVISION,
        source_example_root=EXAMPLE_ROOT,
        models=tuple(models),
        external_models=external_models,
    )


def _external_potential_models(
    text: str,
    definition_evidence: SourceFileEvidence,
    implementation_evidence: SourceFileEvidence,
) -> tuple[ExternalMathematicalModelDeclaration, ...]:
    species: tuple[str, ...] | None = None
    charges: list[str] = []
    pairs: list[tuple[str, str]] = []
    parameters: list[str] = []
    parameter_names_by_pair: dict[tuple[str, str], set[str]] = {}
    active_lines: list[int] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        active_lines.append(line_number)
        key, separator, raw_value = stripped.partition("=")
        if not separator:
            raise ValueError("potential model setting is malformed")
        key = key.strip()
        parts = raw_value.split()
        if key == "potential_elements":
            if species is not None or not parts:
                raise ValueError("potential elements are invalid")
            species = tuple(parts)
        elif key == "potential_charge":
            if len(parts) < 3:
                raise ValueError("potential charge setting is incomplete")
            charges.append(parts[0])
            parameters.append(f"chrg_{parts[0]}")
        elif key == "potential_pair_type":
            if len(parts) != 3 or parts[2] != "buckingham":
                raise ValueError("only the declared Buckingham pair model is supported")
            pair = (parts[0], parts[1])
            pairs.append(pair)
            parameter_names_by_pair[pair] = set()
        elif key == "potential_pair_param":
            if len(parts) < 5:
                raise ValueError("potential pair parameter is incomplete")
            pair = (parts[0], parts[1])
            parameter_name = parts[2]
            if pair not in parameter_names_by_pair:
                raise ValueError("potential parameter precedes its pair declaration")
            parameter_names_by_pair[pair].add(parameter_name)
            parameters.append(f"{pair[0]}{pair[1]}_{parameter_name}")
        else:
            raise ValueError(f"unsupported potential model setting: {key}")
    if species is None or not pairs or not active_lines:
        raise ValueError("Buckingham model declaration is incomplete")
    if len(charges) != len(set(charges)) or set(charges) != set(species):
        raise ValueError("Buckingham charges must cover every species exactly once")
    expected_pairs = {
        (species[first], species[second])
        for first in range(len(species))
        for second in range(first, len(species))
    }
    if set(pairs) != expected_pairs:
        raise ValueError("Buckingham pairs must cover every symmetric interaction")
    if any(
        set(names) != {"A", "rho", "C"} for names in parameter_names_by_pair.values()
    ):
        raise ValueError("Buckingham pair parameters must be A, rho, and C")
    declaration = ExternalMathematicalModelDeclaration(
        name="MgO.buckingham",
        source_model_type="buckingham",
        backend_model="lammps.buck_coul_long",
        species=species,
        pair_interactions=tuple(pairs),
        parameter_variables=tuple(parameters),
        definition_source=MathematicalModelSourceSpan(
            evidence=definition_evidence,
            first_line=min(active_lines),
            last_line=max(active_lines),
        ),
        implementation_source=MathematicalModelSourceSpan(
            evidence=implementation_evidence,
            first_line=77,
            last_line=153,
        ),
    )
    return (declaration,)


def _dependent_parameter_models(
    text: str,
    definition_evidence: SourceFileEvidence,
    implementation_evidence: SourceFileEvidence,
) -> tuple[MathematicalModelDefinition, ...]:
    models: list[MathematicalModelDefinition] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, separator, raw_value = stripped.partition("=")
        if not separator or key.strip() != "potential_charge":
            continue
        parts = raw_value.split()
        if len(parts) < 2 or parts[1] != "equals":
            continue
        if len(parts) != 3:
            raise ValueError("dependent potential charge must have one expression")
        symbol, _relation, expression = parts
        match = _NEGATED_PARAMETER.fullmatch(expression)
        if match is None:
            raise ValueError("only an explicit negated-parameter relation is supported")
        input_variable = match.group(1)
        output_variable = f"chrg_{symbol}"
        models.append(
            MathematicalModelDefinition(
                name=output_variable,
                output_variable=output_variable,
                source_model_type="parameter_dependency",
                kind=MathematicalModelKind.NEGATION,
                inputs=(
                    MathematicalModelInput(
                        alias="value",
                        source_variable=input_variable,
                    ),
                ),
                definition_source=MathematicalModelSourceSpan(
                    evidence=definition_evidence,
                    first_line=line_number,
                    last_line=line_number,
                ),
                implementation_source=MathematicalModelSourceSpan(
                    evidence=implementation_evidence,
                    first_line=269,
                    last_line=274,
                ),
            )
        )
    if not models:
        raise ValueError("the example contains no supported parameter dependency")
    return tuple(models)


def _qoi_models(
    text: str,
    definition_evidence: SourceFileEvidence,
    implementation_evidence: SourceFileEvidence,
) -> tuple[MathematicalModelDefinition, ...]:
    models: list[MathematicalModelDefinition] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, separator, raw_value = stripped.partition("=")
        if not separator or key.strip() != "define_qoi":
            continue
        parts = tuple(part.strip() for part in raw_value.split(","))
        if len(parts) < 3 or any(not part for part in parts):
            raise ValueError("QOI definition is incomplete")
        name, source_model_type, *structures = parts
        kind, inputs, first_line, last_line = _qoi_model_contract(
            name=name,
            source_model_type=source_model_type,
            structures=tuple(structures),
        )
        models.append(
            MathematicalModelDefinition(
                name=name,
                output_variable=name,
                source_model_type=source_model_type,
                kind=kind,
                inputs=inputs,
                definition_source=MathematicalModelSourceSpan(
                    evidence=definition_evidence,
                    first_line=line_number,
                    last_line=line_number,
                ),
                implementation_source=MathematicalModelSourceSpan(
                    evidence=implementation_evidence,
                    first_line=first_line,
                    last_line=last_line,
                ),
            )
        )
    if not models:
        raise ValueError("the example contains no supported QOI model")
    return tuple(models)


def _qoi_model_contract(
    *,
    name: str,
    source_model_type: str,
    structures: tuple[str, ...],
) -> tuple[
    MathematicalModelKind,
    tuple[MathematicalModelInput, ...],
    int,
    int,
]:
    if source_model_type in {"a0", "a1", "a2", "a3", "alpha", "beta", "gamma"}:
        _require_structure_count(source_model_type, structures, 1)
        return (
            MathematicalModelKind.IDENTITY,
            (MathematicalModelInput("value", name),),
            203,
            213,
        )
    if source_model_type in {"c11", "c12", "c44"}:
        _require_structure_count(source_model_type, structures, 1)
        return (
            MathematicalModelKind.IDENTITY,
            (MathematicalModelInput("value", name),),
            215,
            225,
        )
    if source_model_type in {"bulk_modulus", "shear_modulus"}:
        _require_structure_count(source_model_type, structures, 1)
        structure = structures[0]
        kind = (
            MathematicalModelKind.CUBIC_BULK_MODULUS
            if source_model_type == "bulk_modulus"
            else MathematicalModelKind.TETRAGONAL_SHEAR_MODULUS
        )
        line_span = (239, 259) if source_model_type == "bulk_modulus" else (262, 282)
        return (
            kind,
            (
                MathematicalModelInput("c11", f"{structure}.c11"),
                MathematicalModelInput("c12", f"{structure}.c12"),
                MathematicalModelInput(
                    "c44",
                    f"{structure}.c44",
                    participates_in_expression=False,
                ),
            ),
            *line_span,
        )
    if source_model_type == "defect_energy":
        _require_structure_count(source_model_type, structures, 2)
        defect, bulk = structures
        return (
            MathematicalModelKind.DEFECT_FORMATION_ENERGY,
            (
                MathematicalModelInput("defect_energy", f"{defect}.E_min_pos"),
                MathematicalModelInput("defect_atom_count", f"{defect}.n_atoms"),
                MathematicalModelInput("bulk_energy", f"{bulk}.E_min"),
                MathematicalModelInput("bulk_atom_count", f"{bulk}.n_atoms"),
            ),
            284,
            307,
        )
    if source_model_type == "surface_energy":
        _require_structure_count(source_model_type, structures, 2)
        slab, bulk = structures
        return (
            MathematicalModelKind.SURFACE_ENERGY,
            (
                MathematicalModelInput("slab_energy", f"{slab}.E_min_pos"),
                MathematicalModelInput("a1", f"{slab}.a1_min_pos"),
                MathematicalModelInput("a2", f"{slab}.a2_min_pos"),
                MathematicalModelInput("slab_atom_count", f"{slab}.n_atoms"),
                MathematicalModelInput("bulk_energy", f"{bulk}.E_min"),
                MathematicalModelInput("bulk_atom_count", f"{bulk}.n_atoms"),
            ),
            309,
            336,
        )
    raise ValueError(f"unsupported QOI mathematical model: {source_model_type}")


def _require_structure_count(
    source_model_type: str,
    structures: tuple[str, ...],
    expected: int,
) -> None:
    if len(structures) != expected:
        raise ValueError(
            f"{source_model_type} requires exactly {expected} structure(s)"
        )


def _verify_implementation_spans(
    *,
    qoi_implementation_text: str,
    parameter_implementation_text: str,
    lammps_implementation_text: str,
) -> None:
    qoi_lines = qoi_implementation_text.splitlines()
    parameter_lines = parameter_implementation_text.splitlines()
    lammps_lines = lammps_implementation_text.splitlines()
    if len(qoi_lines) < 336 or len(parameter_lines) < 274 or len(lammps_lines) < 153:
        raise ValueError("upstream mathematical-model implementation is incomplete")
    expected_qoi_fragments = (
        "self._predicted_value = self._req_vars[self._qoi_name]",
        "self._predicted_value = (c11+2*c12)/3.",
        "self.predicted_value = (c11-c12)/2.",
        "e_f = e_defect - n_atoms_defect/n_atoms_bulk*e_bulk",
        "e_surf = (e_slab - n_atoms_slab/n_atoms_bulk*e_bulk)/(2*a1*a2)",
    )
    if any(
        fragment not in qoi_implementation_text for fragment in expected_qoi_fragments
    ):
        raise ValueError("upstream QOI implementation no longer matches extraction")
    if "param_dict[pn] = eval(info)" not in "\n".join(parameter_lines[268:274]):
        raise ValueError("upstream parameter dependency implementation changed")
    lammps_span = "\n".join(lammps_lines[76:153])
    if (
        "class BuckinghamPotential(Potential):" not in lammps_span
        or "pair_style buck/coul/long ${R_cut}" not in lammps_span
        or "kspace_style pppm 1.0e-5" not in lammps_span
    ):
        raise ValueError("upstream external Buckingham declaration changed")


def _verified_text(
    checkout_root: Path,
    relative_path: str,
) -> tuple[SourceFileEvidence, str]:
    expected_identity = SOURCE_FILES.get(relative_path)
    if expected_identity is None:
        raise ValueError(f"source binding omits mathematical source: {relative_path}")
    payload = read_bounded_regular_file(
        checkout_root,
        relative_path,
        maximum_bytes=_MAX_SOURCE_BYTES,
        label=f"upstream mathematical source {relative_path}",
    )
    digest = hashlib.sha256(payload).hexdigest()
    expected_digest, expected_size = expected_identity
    if digest != expected_digest or len(payload) != expected_size:
        raise ValueError(f"upstream mathematical source mismatch: {relative_path}")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise ValueError(
            f"upstream mathematical source is not UTF-8: {relative_path}"
        ) from error
    return (
        SourceFileEvidence(
            relative_path=relative_path,
            sha256=digest,
            byte_size=len(payload),
        ),
        text,
    )


__all__ = ["reconstruct_mathematical_models"]
