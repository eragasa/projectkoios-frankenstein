from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import PurePosixPath

from projectkoios.frankensteins.core import SourceFileEvidence, stable_id

_MODEL_CONTRACT_VERSION = "0.1.0"
_IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,255}")
_SOURCE_MODEL_TYPE = re.compile(r"[a-z][a-z0-9_]{0,127}")
_GIT_SHA1 = re.compile(r"[0-9a-f]{40}")


class MathematicalModelKind(StrEnum):
    """Closed arithmetic forms observed in the bound upstream example."""

    IDENTITY = "identity"
    NEGATION = "negation"
    CUBIC_BULK_MODULUS = "cubic_bulk_modulus"
    TETRAGONAL_SHEAR_MODULUS = "tetragonal_shear_modulus"
    DEFECT_FORMATION_ENERGY = "defect_formation_energy"
    SURFACE_ENERGY = "surface_energy"

    @property
    def expression(self) -> str:
        expressions = {
            MathematicalModelKind.IDENTITY: "value",
            MathematicalModelKind.NEGATION: "-value",
            MathematicalModelKind.CUBIC_BULK_MODULUS: ("(c11 + 2 * c12) / 3"),
            MathematicalModelKind.TETRAGONAL_SHEAR_MODULUS: ("(c11 - c12) / 2"),
            MathematicalModelKind.DEFECT_FORMATION_ENERGY: (
                "defect_energy - (defect_atom_count / bulk_atom_count) * bulk_energy"
            ),
            MathematicalModelKind.SURFACE_ENERGY: (
                "(slab_energy - "
                "(slab_atom_count / bulk_atom_count) * bulk_energy) / "
                "(2 * a1 * a2)"
            ),
        }
        return expressions[self]

    @property
    def input_contract(self) -> tuple[tuple[str, bool], ...]:
        contracts = {
            MathematicalModelKind.IDENTITY: (("value", True),),
            MathematicalModelKind.NEGATION: (("value", True),),
            MathematicalModelKind.CUBIC_BULK_MODULUS: (
                ("c11", True),
                ("c12", True),
                ("c44", False),
            ),
            MathematicalModelKind.TETRAGONAL_SHEAR_MODULUS: (
                ("c11", True),
                ("c12", True),
                ("c44", False),
            ),
            MathematicalModelKind.DEFECT_FORMATION_ENERGY: (
                ("defect_energy", True),
                ("defect_atom_count", True),
                ("bulk_energy", True),
                ("bulk_atom_count", True),
            ),
            MathematicalModelKind.SURFACE_ENERGY: (
                ("slab_energy", True),
                ("a1", True),
                ("a2", True),
                ("slab_atom_count", True),
                ("bulk_energy", True),
                ("bulk_atom_count", True),
            ),
        }
        return contracts[self]


@dataclass(frozen=True)
class MathematicalModelSourceSpan:
    """An exact line span in verified upstream source evidence."""

    evidence: SourceFileEvidence
    first_line: int
    last_line: int

    def __post_init__(self) -> None:
        if not isinstance(self.evidence, SourceFileEvidence):
            raise TypeError("evidence must be SourceFileEvidence")
        if not 1 <= self.first_line <= self.last_line <= 1_000_000:
            raise ValueError("mathematical-model source span is invalid")

    def to_dict(self) -> dict[str, object]:
        return {
            "evidence": self.evidence.to_dict(),
            "first_line": self.first_line,
            "last_line": self.last_line,
        }


@dataclass(frozen=True)
class MathematicalModelInput:
    """One bound input, including source-required but unused inputs."""

    alias: str
    source_variable: str
    participates_in_expression: bool = True

    def __post_init__(self) -> None:
        if _IDENTIFIER.fullmatch(self.alias) is None:
            raise ValueError("mathematical-model input alias is invalid")
        if _IDENTIFIER.fullmatch(self.source_variable) is None:
            raise ValueError("mathematical-model source variable is invalid")
        if not isinstance(self.participates_in_expression, bool):
            raise TypeError("participates_in_expression must be boolean")

    def to_dict(self) -> dict[str, object]:
        return {
            "alias": self.alias,
            "source_variable": self.source_variable,
            "participates_in_expression": self.participates_in_expression,
        }


@dataclass(frozen=True)
class MathematicalModelDefinition:
    """One safe scalar rewrite of an observed upstream mathematical model."""

    name: str
    output_variable: str
    source_model_type: str
    kind: MathematicalModelKind
    inputs: tuple[MathematicalModelInput, ...]
    definition_source: MathematicalModelSourceSpan
    implementation_source: MathematicalModelSourceSpan | None
    contract_version: str = _MODEL_CONTRACT_VERSION
    scientific_validation_claimed: bool = False
    model_id: str = field(init=False)

    def __post_init__(self) -> None:
        if _IDENTIFIER.fullmatch(self.name) is None:
            raise ValueError("mathematical-model name is invalid")
        if _IDENTIFIER.fullmatch(self.output_variable) is None:
            raise ValueError("mathematical-model output variable is invalid")
        if _SOURCE_MODEL_TYPE.fullmatch(self.source_model_type) is None:
            raise ValueError("source model type is invalid")
        if not isinstance(self.kind, MathematicalModelKind):
            raise TypeError("kind must be MathematicalModelKind")
        if not isinstance(self.inputs, tuple):
            raise TypeError("mathematical-model inputs must be a tuple")
        if any(not isinstance(item, MathematicalModelInput) for item in self.inputs):
            raise TypeError("mathematical-model inputs contain an invalid value")
        observed_contract = tuple(
            (item.alias, item.participates_in_expression) for item in self.inputs
        )
        if observed_contract != self.kind.input_contract:
            raise ValueError("mathematical-model inputs do not match its kind")
        variables = tuple(item.source_variable for item in self.inputs)
        if len(variables) != len(set(variables)):
            raise ValueError("mathematical-model source variables must be unique")
        if not isinstance(self.definition_source, MathematicalModelSourceSpan):
            raise TypeError("definition_source must be a source span")
        if self.implementation_source is not None and not isinstance(
            self.implementation_source, MathematicalModelSourceSpan
        ):
            raise TypeError("implementation_source must be a source span")
        if self.contract_version != _MODEL_CONTRACT_VERSION:
            raise ValueError("unsupported mathematical-model contract version")
        if self.scientific_validation_claimed:
            raise ValueError(
                "an extracted mathematical model cannot claim scientific validation"
            )
        object.__setattr__(
            self,
            "model_id",
            stable_id("mathematical-model", self._identity_dict()),
        )

    @property
    def expression(self) -> str:
        return self.kind.expression

    @property
    def unused_required_inputs(self) -> tuple[MathematicalModelInput, ...]:
        return tuple(
            item for item in self.inputs if not item.participates_in_expression
        )

    def evaluate(self, values: Mapping[str, int | float]) -> float:
        """Evaluate only the closed arithmetic form, never a source expression."""
        if not isinstance(values, Mapping):
            raise TypeError("mathematical-model values must be a mapping")
        expected = tuple(item.source_variable for item in self.inputs)
        if set(values) != set(expected) or len(values) != len(expected):
            raise ValueError("mathematical-model values must exactly match inputs")
        ordered = tuple(
            self._finite(item.source_variable, values[item.source_variable])
            for item in self.inputs
        )

        if self.kind is MathematicalModelKind.IDENTITY:
            result = ordered[0]
        elif self.kind is MathematicalModelKind.NEGATION:
            result = -ordered[0]
        elif self.kind is MathematicalModelKind.CUBIC_BULK_MODULUS:
            c11, c12, _c44 = ordered
            result = (c11 + 2.0 * c12) / 3.0
        elif self.kind is MathematicalModelKind.TETRAGONAL_SHEAR_MODULUS:
            c11, c12, _c44 = ordered
            result = (c11 - c12) / 2.0
        elif self.kind is MathematicalModelKind.DEFECT_FORMATION_ENERGY:
            defect_energy, defect_count, bulk_energy, bulk_count = ordered
            self._nonzero("bulk_atom_count", bulk_count)
            result = defect_energy - defect_count / bulk_count * bulk_energy
        elif self.kind is MathematicalModelKind.SURFACE_ENERGY:
            slab_energy, a1, a2, slab_count, bulk_energy, bulk_count = ordered
            self._nonzero("a1", a1)
            self._nonzero("a2", a2)
            self._nonzero("bulk_atom_count", bulk_count)
            result = (slab_energy - slab_count / bulk_count * bulk_energy) / (
                2.0 * a1 * a2
            )
        else:  # pragma: no cover - StrEnum exhaustiveness guard
            raise AssertionError("unsupported mathematical-model kind")
        return self._finite("model result", result)

    @staticmethod
    def _finite(name: str, value: object) -> float:
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise TypeError(f"{name} must be a finite number")
        normalized = float(value)
        if not math.isfinite(normalized):
            raise ValueError(f"{name} must be a finite number")
        return 0.0 if normalized == 0.0 else normalized

    @staticmethod
    def _nonzero(name: str, value: float) -> None:
        if value == 0.0:
            raise ValueError(f"{name} cannot be zero")

    def _identity_dict(self) -> dict[str, object]:
        return {
            "contract": "projectkoios.mathematical-model",
            "contract_version": self.contract_version,
            "name": self.name,
            "output_variable": self.output_variable,
            "source_model_type": self.source_model_type,
            "kind": self.kind.value,
            "expression": self.expression,
            "inputs": [item.to_dict() for item in self.inputs],
            "definition_source": self.definition_source.to_dict(),
            "implementation_source": (
                None
                if self.implementation_source is None
                else self.implementation_source.to_dict()
            ),
            "scientific_validation_claimed": self.scientific_validation_claimed,
        }

    def to_dict(self) -> dict[str, object]:
        return {**self._identity_dict(), "model_id": self.model_id}


@dataclass(frozen=True)
class ExternalMathematicalModelDeclaration:
    """A model selected by evidence but delegated to an external backend."""

    name: str
    source_model_type: str
    backend_model: str
    species: tuple[str, ...]
    pair_interactions: tuple[tuple[str, str], ...]
    parameter_variables: tuple[str, ...]
    definition_source: MathematicalModelSourceSpan
    implementation_source: MathematicalModelSourceSpan
    contract_version: str = _MODEL_CONTRACT_VERSION
    evaluation_supported: bool = False
    scientific_validation_claimed: bool = False
    model_id: str = field(init=False)

    def __post_init__(self) -> None:
        if _IDENTIFIER.fullmatch(self.name) is None:
            raise ValueError("external mathematical-model name is invalid")
        if _SOURCE_MODEL_TYPE.fullmatch(self.source_model_type) is None:
            raise ValueError("external source model type is invalid")
        if _IDENTIFIER.fullmatch(self.backend_model) is None:
            raise ValueError("external backend model is invalid")
        if not self.species or len(self.species) > 64:
            raise ValueError("external model species are invalid")
        if any(_IDENTIFIER.fullmatch(item) is None for item in self.species):
            raise ValueError("external model species contain an invalid value")
        if len(self.species) != len(set(self.species)):
            raise ValueError("external model species must be unique")
        if not self.pair_interactions or len(self.pair_interactions) > 2_048:
            raise ValueError("external model pair interactions are invalid")
        if any(
            len(pair) != 2 or pair[0] not in self.species or pair[1] not in self.species
            for pair in self.pair_interactions
        ):
            raise ValueError("external model pair interaction is invalid")
        if len(self.pair_interactions) != len(set(self.pair_interactions)):
            raise ValueError("external model pair interactions must be unique")
        if not self.parameter_variables or len(self.parameter_variables) > 10_000:
            raise ValueError("external model parameter variables are invalid")
        if any(
            _IDENTIFIER.fullmatch(item) is None for item in self.parameter_variables
        ):
            raise ValueError("external model parameter variable is invalid")
        if len(self.parameter_variables) != len(set(self.parameter_variables)):
            raise ValueError("external model parameter variables must be unique")
        if not isinstance(self.definition_source, MathematicalModelSourceSpan):
            raise TypeError("definition_source must be a source span")
        if not isinstance(self.implementation_source, MathematicalModelSourceSpan):
            raise TypeError("implementation_source must be a source span")
        if self.contract_version != _MODEL_CONTRACT_VERSION:
            raise ValueError("unsupported external model contract version")
        if self.evaluation_supported:
            raise ValueError("an external model cannot claim local evaluation support")
        if self.scientific_validation_claimed:
            raise ValueError(
                "an extracted mathematical model cannot claim scientific validation"
            )
        object.__setattr__(
            self,
            "model_id",
            stable_id("external-mathematical-model", self._identity_dict()),
        )

    def _identity_dict(self) -> dict[str, object]:
        return {
            "contract": "projectkoios.external-mathematical-model",
            "contract_version": self.contract_version,
            "name": self.name,
            "source_model_type": self.source_model_type,
            "backend_model": self.backend_model,
            "species": list(self.species),
            "pair_interactions": [list(pair) for pair in self.pair_interactions],
            "parameter_variables": list(self.parameter_variables),
            "definition_source": self.definition_source.to_dict(),
            "implementation_source": self.implementation_source.to_dict(),
            "evaluation_supported": self.evaluation_supported,
            "scientific_validation_claimed": self.scientific_validation_claimed,
        }

    def to_dict(self) -> dict[str, object]:
        return {**self._identity_dict(), "model_id": self.model_id}


@dataclass(frozen=True)
class MathematicalModelCatalog:
    """Ordered mathematical models selected by one exact upstream example."""

    source_component: str
    source_revision: str
    source_example_root: str
    models: tuple[MathematicalModelDefinition, ...]
    external_models: tuple[ExternalMathematicalModelDeclaration, ...]
    contract_version: str = _MODEL_CONTRACT_VERSION
    catalog_id: str = field(init=False)

    def __post_init__(self) -> None:
        if _SOURCE_MODEL_TYPE.fullmatch(self.source_component) is None:
            raise ValueError("mathematical-model source component is invalid")
        if _GIT_SHA1.fullmatch(self.source_revision) is None:
            raise ValueError("source revision must be an exact Git SHA-1")
        example_path = PurePosixPath(self.source_example_root)
        if (
            not self.source_example_root
            or len(self.source_example_root) > 1_000
            or self.source_example_root != example_path.as_posix()
            or example_path.is_absolute()
            or "." in example_path.parts
            or ".." in example_path.parts
        ):
            raise ValueError("source example root is invalid")
        if not isinstance(self.models, tuple) or not self.models:
            raise ValueError("mathematical-model catalog cannot be empty")
        if len(self.models) > 1_000:
            raise ValueError("mathematical-model catalog exceeds its bound")
        if any(
            not isinstance(item, MathematicalModelDefinition) for item in self.models
        ):
            raise TypeError("mathematical-model catalog contains an invalid value")
        if not isinstance(self.external_models, tuple):
            raise TypeError("external mathematical models must be a tuple")
        if len(self.external_models) > 1_000:
            raise ValueError("external mathematical models exceed their bound")
        if any(
            not isinstance(item, ExternalMathematicalModelDeclaration)
            for item in self.external_models
        ):
            raise TypeError("external mathematical models contain an invalid value")
        names = tuple(item.name for item in self.models)
        external_names = tuple(item.name for item in self.external_models)
        outputs = tuple(item.output_variable for item in self.models)
        if len(names) != len(set(names)):
            raise ValueError("mathematical-model names must be unique")
        if len(external_names) != len(set(external_names)):
            raise ValueError("external mathematical-model names must be unique")
        if set(names) & set(external_names):
            raise ValueError("local and external model names must be distinct")
        if len(outputs) != len(set(outputs)):
            raise ValueError("mathematical-model outputs must be unique")
        if self.contract_version != _MODEL_CONTRACT_VERSION:
            raise ValueError("unsupported mathematical-model catalog version")
        object.__setattr__(
            self,
            "catalog_id",
            stable_id("mathematical-model-catalog", self._identity_dict()),
        )

    def model(self, name: str) -> MathematicalModelDefinition:
        for model in self.models:
            if model.name == name:
                return model
        raise KeyError(name)

    def _identity_dict(self) -> dict[str, object]:
        return {
            "contract": "projectkoios.mathematical-model-catalog",
            "contract_version": self.contract_version,
            "source_component": self.source_component,
            "source_revision": self.source_revision,
            "source_example_root": self.source_example_root,
            "models": [item.to_dict() for item in self.models],
            "external_models": [item.to_dict() for item in self.external_models],
        }

    def to_dict(self) -> dict[str, object]:
        return {**self._identity_dict(), "catalog_id": self.catalog_id}


__all__ = [
    "ExternalMathematicalModelDeclaration",
    "MathematicalModelCatalog",
    "MathematicalModelDefinition",
    "MathematicalModelInput",
    "MathematicalModelKind",
    "MathematicalModelSourceSpan",
]
