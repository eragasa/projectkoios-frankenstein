from __future__ import annotations

import ast
import hashlib
import json
import os
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import yaml  # type: ignore[import-untyped]
from yaml.constructor import ConstructorError  # type: ignore[import-untyped]

LEGACY_ORDERED_DICT_TAG: Final = (
    "tag:yaml.org,2002:python/object/apply:collections.OrderedDict"
)
SUPPORTED_SAMPLING_MODES: Final = frozenset({"parametric", "kde", "from_file"})
KNOWN_BROKEN_SAMPLING_MODES: Final = {
    "kde_w_clusters": "the source implementation references undefined _mc_config"
}
SUPPORTED_QOI_TYPES: Final = frozenset(
    {
        "E_formation",
        "E_surface",
        "a11_min_all",
        "bulk_modulus",
        "c11",
        "c12",
        "c44",
        "shear_modulus",
    }
)
BUCKINGHAM_PARAMETER_SUFFIXES: Final = ("A", "rho", "C")
_ALLOWED_EXPRESSION_NODES: Final = (
    ast.Expression,
    ast.Compare,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.UnaryOp,
    ast.UAdd,
    ast.USub,
    ast.BinOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
)


class ConfigurationError(ValueError):
    """Raised when a source or execution configuration is invalid."""


class _LegacyOrderedDictLoader(yaml.SafeLoader):  # type: ignore[misc]
    """Safe loader extended for one exact historical OrderedDict tag."""


def _construct_legacy_ordered_dict(
    loader: yaml.SafeLoader, node: yaml.Node
) -> OrderedDict[Any, Any]:
    values = loader.construct_sequence(node, deep=True)
    if len(values) != 1 or not isinstance(values[0], list):
        raise ConstructorError(
            None,
            None,
            "historical OrderedDict value must contain one pair sequence",
            node.start_mark,
        )
    try:
        return OrderedDict(values[0])
    except (TypeError, ValueError) as error:
        raise ConstructorError(
            None,
            None,
            "historical OrderedDict value contains invalid pairs",
            node.start_mark,
        ) from error


_LegacyOrderedDictLoader.add_constructor(
    LEGACY_ORDERED_DICT_TAG,
    _construct_legacy_ordered_dict,
)


def configure_pypospack_legacy_yaml_loader() -> None:
    """Teach the pinned PyPosPack loader only its historical OrderedDict tag."""

    from pypospack.io.filesystem import (  # type: ignore[import-untyped]
        OrderedDictYAMLLoader,
    )

    OrderedDictYAMLLoader.add_constructor(
        LEGACY_ORDERED_DICT_TAG,
        _construct_legacy_ordered_dict,
    )


def _require_mapping(value: object, location: str) -> Mapping[object, object]:
    if not isinstance(value, Mapping):
        raise ConfigurationError(f"{location} must be a mapping")
    return value


def _require_string(value: object, location: str) -> str:
    if not isinstance(value, str) or not value:
        raise ConfigurationError(f"{location} must be a non-empty string")
    return value


def _require_integer(value: object, location: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ConfigurationError(f"{location} must be an integer >= {minimum}")
    return value


def _require_number(value: object, location: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ConfigurationError(f"{location} must be numeric")
    return float(value)


def _require_relative_path(value: object, location: str) -> str:
    raw_path = _require_string(value, location)
    path = Path(raw_path)
    if path.is_absolute() or ".." in path.parts:
        raise ConfigurationError(f"{location} must be a contained relative path")
    return raw_path


def _validate_expression(
    expression: str,
    *,
    location: str,
    parameter_names: frozenset[str],
    require_comparison: bool,
) -> None:
    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise ConfigurationError(f"{location} is not a valid expression") from error
    if require_comparison and not isinstance(parsed.body, ast.Compare):
        raise ConfigurationError(f"{location} must be a comparison")
    for node in ast.walk(parsed):
        if not isinstance(node, _ALLOWED_EXPRESSION_NODES):
            raise ConfigurationError(
                f"{location} contains unsupported expression syntax"
            )
        if isinstance(node, ast.Name) and node.id not in parameter_names:
            raise ConfigurationError(
                f"{location} references unknown parameter {node.id!r}"
            )
        if isinstance(node, ast.Constant) and (
            isinstance(node.value, bool) or not isinstance(node.value, int | float)
        ):
            raise ConfigurationError(f"{location} contains a non-numeric literal")


def _expected_buckingham_parameters(symbols: tuple[str, ...]) -> frozenset[str]:
    names = {f"chrg_{symbol}" for symbol in symbols}
    for index, first in enumerate(symbols):
        for second in symbols[index:]:
            names.update(
                f"{first}{second}_{suffix}" for suffix in BUCKINGHAM_PARAMETER_SUFFIXES
            )
    return frozenset(names)


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_plain(item) for item in value]
    return value


@dataclass(frozen=True)
class QoiConfiguration:
    name: str
    qoi_type: str
    structures: tuple[tuple[str, str], ...]
    target: float

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "qoi_type": self.qoi_type,
            "structures": dict(self.structures),
            "target": self.target,
        }


@dataclass(frozen=True)
class StructureConfiguration:
    name: str
    filename: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "filename": self.filename}


@dataclass(frozen=True)
class PotentialConfiguration:
    potential_type: str
    symbols: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "potential_type": self.potential_type,
            "symbols": list(self.symbols),
        }


@dataclass(frozen=True)
class IterationConfiguration:
    index: int
    mode: str
    n_samples: int
    source_file: str | None = None

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "index": self.index,
            "mode": self.mode,
            "n_samples": self.n_samples,
        }
        if self.source_file is not None:
            result["source_file"] = self.source_file
        return result


@dataclass(frozen=True)
class ParameterDistribution:
    name: str
    mode: str
    specification: object

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "mode": self.mode,
            "specification": _plain(self.specification),
        }


@dataclass(frozen=True)
class MgOBuckinghamConfiguration:
    source_path: Path
    source_sha256: str
    qois: tuple[QoiConfiguration, ...]
    qoi_constraints: tuple[tuple[str, object], ...]
    structure_directory: str
    structures: tuple[StructureConfiguration, ...]
    potential: PotentialConfiguration
    iterations: tuple[IterationConfiguration, ...]
    mc_seed: int | None
    parameter_distributions: tuple[ParameterDistribution, ...]
    parameter_constraints: tuple[tuple[str, str], ...]

    @classmethod
    def from_legacy_file(
        cls,
        path: str | Path,
        *,
        expected_sha256: str | None = None,
    ) -> MgOBuckinghamConfiguration:
        source_path = Path(path).resolve()
        source_bytes = source_path.read_bytes()
        source_sha256 = hashlib.sha256(source_bytes).hexdigest()
        if expected_sha256 is not None and source_sha256 != expected_sha256:
            raise ConfigurationError(
                "source configuration SHA-256 does not match provenance"
            )

        try:
            raw = yaml.load(source_bytes, Loader=_LegacyOrderedDictLoader)
        except yaml.YAMLError as error:
            raise ConfigurationError("source configuration is invalid YAML") from error
        root = _require_mapping(raw, "configuration")

        qois_raw = _require_mapping(root.get("qois"), "qois")
        qois: list[QoiConfiguration] = []
        for raw_name, raw_qoi in qois_raw.items():
            name = _require_string(raw_name, "qoi name")
            qoi = _require_mapping(raw_qoi, f"qois.{name}")
            qoi_structures = _require_mapping(
                qoi.get("structures"), f"qois.{name}.structures"
            )
            qoi_type = _require_string(qoi.get("qoi_type"), f"qois.{name}.qoi_type")
            if qoi_type not in SUPPORTED_QOI_TYPES:
                raise ConfigurationError(
                    f"qois.{name}.qoi_type has unsupported type {qoi_type!r}"
                )
            qois.append(
                QoiConfiguration(
                    name=name,
                    qoi_type=qoi_type,
                    structures=tuple(
                        (
                            _require_string(role, f"qois.{name}.structures role"),
                            _require_string(
                                structure, f"qois.{name}.structures.{role}"
                            ),
                        )
                        for role, structure in qoi_structures.items()
                    ),
                    target=_require_number(qoi.get("target"), f"qois.{name}.target"),
                )
            )

        structure_section = _require_mapping(root.get("structures"), "structures")
        structures_raw = _require_mapping(
            structure_section.get("structures"), "structures.structures"
        )
        structure_definitions = tuple(
            StructureConfiguration(
                name=_require_string(name, "structure name"),
                filename=_require_relative_path(
                    filename, f"structures.structures.{name}"
                ),
            )
            for name, filename in structures_raw.items()
        )
        structure_names = {structure.name for structure in structure_definitions}
        for qoi_configuration in qois:
            for _, structure_name in qoi_configuration.structures:
                if structure_name not in structure_names:
                    raise ConfigurationError(
                        f"qoi {qoi_configuration.name} references unknown structure "
                        f"{structure_name}"
                    )

        potential_raw = _require_mapping(root.get("potential"), "potential")
        symbols_raw = potential_raw.get("symbols")
        if not isinstance(symbols_raw, Sequence) or isinstance(symbols_raw, str):
            raise ConfigurationError("potential.symbols must be a sequence")
        potential = PotentialConfiguration(
            potential_type=_require_string(
                potential_raw.get("potential_type"), "potential.potential_type"
            ),
            symbols=tuple(
                _require_string(symbol, "potential.symbols item")
                for symbol in symbols_raw
            ),
        )
        if potential.potential_type != "buckingham":
            raise ConfigurationError("potential.potential_type must be 'buckingham'")
        if potential.symbols != ("Mg", "O"):
            raise ConfigurationError("potential.symbols must be ['Mg', 'O']")

        sampling_raw = _require_mapping(root.get("sampling_type"), "sampling_type")
        n_iterations = _require_integer(
            sampling_raw.get("n_iterations"), "sampling_type.n_iterations", minimum=1
        )
        mc_seed_raw = sampling_raw.get("mc_seed")
        mc_seed = (
            None
            if mc_seed_raw is None
            else _require_integer(mc_seed_raw, "sampling_type.mc_seed")
        )
        iterations: list[IterationConfiguration] = []
        for index in range(n_iterations):
            iteration_raw = _require_mapping(
                sampling_raw.get(index), f"sampling_type.{index}"
            )
            mode = _require_string(
                iteration_raw.get("type"), f"sampling_type.{index}.type"
            )
            if mode in KNOWN_BROKEN_SAMPLING_MODES:
                raise ConfigurationError(
                    f"sampling_type.{index}.type {mode!r} is unsupported: "
                    f"{KNOWN_BROKEN_SAMPLING_MODES[mode]}"
                )
            if mode not in SUPPORTED_SAMPLING_MODES:
                raise ConfigurationError(
                    f"sampling_type.{index}.type has unknown mode {mode!r}"
                )
            source_file_raw = iteration_raw.get("file")
            source_file = (
                None
                if source_file_raw is None
                else _require_relative_path(
                    source_file_raw, f"sampling_type.{index}.file"
                )
            )
            if mode == "from_file" and source_file is None:
                raise ConfigurationError(
                    f"sampling_type.{index}.file is required for from_file"
                )
            iterations.append(
                IterationConfiguration(
                    index=index,
                    mode=mode,
                    n_samples=_require_integer(
                        iteration_raw.get("n_samples"),
                        f"sampling_type.{index}.n_samples",
                        minimum=1,
                    ),
                    source_file=source_file,
                )
            )

        distributions_raw = _require_mapping(root.get("sampling_dist"), "sampling_dist")
        parameter_names = frozenset(
            _require_string(name, "sampling distribution name")
            for name in distributions_raw
        )
        expected_parameter_names = _expected_buckingham_parameters(potential.symbols)
        if parameter_names != expected_parameter_names:
            missing = sorted(expected_parameter_names - parameter_names)
            unexpected = sorted(parameter_names - expected_parameter_names)
            raise ConfigurationError(
                "sampling_dist does not match Buckingham parameters; "
                f"missing={missing}, unexpected={unexpected}"
            )
        distributions: list[ParameterDistribution] = []
        for raw_name, raw_distribution in distributions_raw.items():
            name = _require_string(raw_name, "sampling distribution name")
            location = f"sampling_dist.{name}"
            if (
                not isinstance(raw_distribution, Sequence)
                or isinstance(raw_distribution, str | bytes)
                or len(raw_distribution) != 2
            ):
                raise ConfigurationError(f"{location} must have two items")
            mode = _require_string(raw_distribution[0], f"{location}.mode")
            specification = raw_distribution[1]
            if mode == "uniform":
                bounds = _require_mapping(specification, f"{location}.specification")
                if set(bounds) != {"a", "b"}:
                    raise ConfigurationError(
                        f"{location}.specification must contain only a and b"
                    )
                lower = _require_number(bounds["a"], f"{location}.a")
                upper = _require_number(bounds["b"], f"{location}.b")
                if lower >= upper:
                    raise ConfigurationError(f"{location} requires a < b")
            elif mode == "equals":
                if isinstance(specification, str):
                    _validate_expression(
                        specification,
                        location=f"{location}.specification",
                        parameter_names=parameter_names,
                        require_comparison=False,
                    )
                else:
                    _require_number(specification, f"{location}.specification")
            else:
                raise ConfigurationError(
                    f"{location}.mode has unsupported mode {mode!r}"
                )
            distributions.append(
                ParameterDistribution(
                    name=name,
                    mode=mode,
                    specification=specification,
                )
            )

        qoi_constraints_raw = _require_mapping(
            root.get("qoi_constraints"), "qoi_constraints"
        )
        parameter_constraints_raw = _require_mapping(
            root.get("sampling_constraints"), "sampling_constraints"
        )
        if set(qoi_constraints_raw) != {"select_pareto_only"} or not isinstance(
            qoi_constraints_raw["select_pareto_only"], bool
        ):
            raise ConfigurationError(
                "qoi_constraints must contain one boolean select_pareto_only setting"
            )
        for raw_name, raw_constraint in parameter_constraints_raw.items():
            constraint_name = _require_string(raw_name, "sampling constraint name")
            constraint = _require_string(
                raw_constraint, f"sampling_constraints.{constraint_name}"
            )
            _validate_expression(
                constraint,
                location=f"sampling_constraints.{constraint_name}",
                parameter_names=parameter_names,
                require_comparison=True,
            )

        return cls(
            source_path=source_path,
            source_sha256=source_sha256,
            qois=tuple(qois),
            qoi_constraints=tuple(
                (str(name), _plain(value))
                for name, value in qoi_constraints_raw.items()
            ),
            structure_directory=_require_relative_path(
                structure_section.get("structure_directory"),
                "structures.structure_directory",
            ),
            structures=structure_definitions,
            potential=potential,
            iterations=tuple(iterations),
            mc_seed=mc_seed,
            parameter_distributions=tuple(distributions),
            parameter_constraints=tuple(
                (
                    _require_string(name, "sampling constraint name"),
                    _require_string(value, f"sampling_constraints.{name}"),
                )
                for name, value in parameter_constraints_raw.items()
            ),
        )

    def validate_structure_files(self, work_directory: str | Path) -> None:
        structure_root = Path(work_directory) / self.structure_directory
        missing = [
            structure.filename
            for structure in self.structures
            if not structure_root.joinpath(structure.filename).is_file()
        ]
        if missing:
            raise ConfigurationError(
                "missing structure files: " + ", ".join(sorted(missing))
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "source_path": self.source_path.as_posix(),
            "source_sha256": self.source_sha256,
            "qois": [qoi.to_dict() for qoi in self.qois],
            "qoi_constraints": dict(self.qoi_constraints),
            "structure_directory": self.structure_directory,
            "structures": [structure.to_dict() for structure in self.structures],
            "potential": self.potential.to_dict(),
            "iterations": [iteration.to_dict() for iteration in self.iterations],
            "mc_seed": self.mc_seed,
            "parameter_distributions": [
                distribution.to_dict() for distribution in self.parameter_distributions
            ],
            "parameter_constraints": dict(self.parameter_constraints),
        }


@dataclass(frozen=True)
class ExecutionConfiguration:
    work_directory: Path
    data_directory: Path
    lammps_binary: Path | None = None
    lammps_version: str | None = None
    mpi_size: int = 1
    restart: bool = False
    log_to_stdout: bool = True

    def __post_init__(self) -> None:
        work_directory = self.work_directory.resolve()
        data_directory = self.data_directory
        if not data_directory.is_absolute():
            data_directory = work_directory / data_directory
        lammps_binary = self.lammps_binary
        if lammps_binary is not None and not lammps_binary.is_absolute():
            lammps_binary = work_directory / lammps_binary
        if self.mpi_size < 1:
            raise ConfigurationError("mpi_size must be at least one")
        object.__setattr__(self, "work_directory", work_directory)
        object.__setattr__(self, "data_directory", data_directory.resolve())
        object.__setattr__(
            self,
            "lammps_binary",
            None if lammps_binary is None else lammps_binary.resolve(),
        )

    @classmethod
    def from_environment(
        cls,
        *,
        work_directory: str | Path,
        data_directory: str | Path = "data",
        mpi_size: int = 1,
        restart: bool = False,
        log_to_stdout: bool = True,
    ) -> ExecutionConfiguration:
        raw_lammps_binary = os.environ.get("LAMMPS_BIN")
        return cls(
            work_directory=Path(work_directory),
            data_directory=Path(data_directory),
            lammps_binary=(
                None if raw_lammps_binary is None else Path(raw_lammps_binary)
            ),
            lammps_version=os.environ.get("LAMMPS_VERSION"),
            mpi_size=mpi_size,
            restart=restart,
            log_to_stdout=log_to_stdout,
        )

    def validate(self, *, require_lammps: bool = True) -> None:
        if not self.work_directory.is_dir():
            raise ConfigurationError("work_directory does not exist")
        if require_lammps:
            if self.lammps_binary is None:
                raise ConfigurationError("LAMMPS_BIN is required")
            if not self.lammps_binary.is_file():
                raise ConfigurationError("LAMMPS_BIN does not name a file")
            if not os.access(self.lammps_binary, os.X_OK):
                raise ConfigurationError("LAMMPS_BIN is not executable")

    def to_dict(self) -> dict[str, object]:
        return {
            "work_directory": self.work_directory.as_posix(),
            "data_directory": self.data_directory.as_posix(),
            "lammps_binary": (
                None if self.lammps_binary is None else self.lammps_binary.as_posix()
            ),
            "lammps_version": self.lammps_version,
            "mpi_size": self.mpi_size,
            "restart": self.restart,
            "log_to_stdout": self.log_to_stdout,
        }


def write_resolved_snapshot(
    path: str | Path,
    *,
    scientific: MgOBuckinghamConfiguration,
    execution: ExecutionConfiguration,
    source_revision: str,
    source_tree: str,
    random_seed: int,
) -> None:
    if random_seed < 0:
        raise ConfigurationError("random_seed must be non-negative")
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "schema_version": 1,
        "source": {
            "component": "pypospack",
            "revision": source_revision,
            "tree": source_tree,
        },
        "scientific": scientific.to_dict(),
        "execution": execution.to_dict(),
        "random_seed": random_seed,
    }
    temporary = destination.with_name(f".{destination.name}.tmp")
    temporary.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(destination)


__all__ = [
    "ConfigurationError",
    "ExecutionConfiguration",
    "IterationConfiguration",
    "KNOWN_BROKEN_SAMPLING_MODES",
    "MgOBuckinghamConfiguration",
    "ParameterDistribution",
    "PotentialConfiguration",
    "QoiConfiguration",
    "SUPPORTED_SAMPLING_MODES",
    "StructureConfiguration",
    "configure_pypospack_legacy_yaml_loader",
    "write_resolved_snapshot",
]
