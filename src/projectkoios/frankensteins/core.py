from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from projectkoios.frankensteins.mathematics.models import (
        MathematicalModelCatalog,
    )

_SHA256 = re.compile(r"[0-9a-f]{64}")
_GIT_SHA1 = re.compile(r"[0-9a-f]{40}")
_NAME = re.compile(r"[a-z][a-z0-9_.-]{0,127}")


def canonical_json_bytes(value: object) -> bytes:
    """Serialize identity material without environment-dependent formatting."""
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def stable_id(kind: str, value: object) -> str:
    if _NAME.fullmatch(kind) is None:
        raise ValueError("stable-ID kind is invalid")
    digest = hashlib.sha256(canonical_json_bytes(value)).hexdigest()
    return f"{kind}:sha256:{digest}"


def _relative_path(value: str, field_name: str) -> str:
    path = PurePosixPath(value)
    if (
        not value
        or value != path.as_posix()
        or path.is_absolute()
        or ".." in path.parts
        or "." in path.parts
    ):
        raise ValueError(f"{field_name} must be a normalized relative path")
    return value


@dataclass(frozen=True)
class SourceFileEvidence:
    relative_path: str
    sha256: str
    byte_size: int

    def __post_init__(self) -> None:
        _relative_path(self.relative_path, "relative_path")
        if _SHA256.fullmatch(self.sha256) is None:
            raise ValueError("sha256 must be 64 lowercase hexadecimal characters")
        if not 0 <= self.byte_size <= 1_000_000_000:
            raise ValueError("byte_size is outside the reconstruction bound")

    def to_dict(self) -> dict[str, object]:
        return {
            "relative_path": self.relative_path,
            "sha256": self.sha256,
            "byte_size": self.byte_size,
        }


@dataclass(frozen=True)
class ObservedSetting:
    key: str
    values: tuple[str, ...]
    evidence_path: str
    line_number: int

    def __post_init__(self) -> None:
        if _NAME.fullmatch(self.key) is None:
            raise ValueError("setting key is invalid")
        if not self.values or len(self.values) > 32:
            raise ValueError("setting values are outside the reconstruction bound")
        if any(not value or len(value) > 512 for value in self.values):
            raise ValueError("setting value is invalid")
        _relative_path(self.evidence_path, "evidence_path")
        if not 1 <= self.line_number <= 1_000_000:
            raise ValueError("line_number is invalid")

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "values": list(self.values),
            "evidence_path": self.evidence_path,
            "line_number": self.line_number,
        }


@dataclass(frozen=True)
class RecipeWarning:
    code: str
    evidence_paths: tuple[str, ...]
    detail: str

    def __post_init__(self) -> None:
        if _NAME.fullmatch(self.code) is None:
            raise ValueError("warning code is invalid")
        if not self.evidence_paths or len(self.evidence_paths) > 64:
            raise ValueError("warning evidence is invalid")
        for path in self.evidence_paths:
            _relative_path(path, "warning evidence path")
        if not self.detail or len(self.detail) > 1_000:
            raise ValueError("warning detail is invalid")

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "evidence_paths": list(self.evidence_paths),
            "detail": self.detail,
        }


@dataclass(frozen=True)
class IntegrationObservation:
    integration: str
    contract_version: str
    payload_json: str

    def __post_init__(self) -> None:
        if _NAME.fullmatch(self.integration) is None:
            raise ValueError("integration name is invalid")
        if not self.contract_version or len(self.contract_version) > 64:
            raise ValueError("integration contract version is invalid")
        try:
            payload = json.loads(self.payload_json)
        except json.JSONDecodeError as error:
            raise ValueError("integration payload is invalid JSON") from error
        if not isinstance(payload, dict):
            raise ValueError("integration payload must be an object")
        if canonical_json_bytes(payload).decode("utf-8") != self.payload_json:
            raise ValueError("integration payload must be canonical JSON")

    @classmethod
    def from_payload(
        cls,
        *,
        integration: str,
        contract_version: str,
        payload: dict[str, object],
    ) -> IntegrationObservation:
        return cls(
            integration=integration,
            contract_version=contract_version,
            payload_json=canonical_json_bytes(payload).decode("utf-8"),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "integration": self.integration,
            "contract_version": self.contract_version,
            "payload": json.loads(self.payload_json),
        }


@dataclass(frozen=True)
class FrankensteinRecipe:
    engine_name: str
    source_component: str
    source_repository_url: str
    source_revision: str
    source_tree: str
    source_example_root: str
    source_license_path: str
    source_license_sha256: str
    source_files: tuple[SourceFileEvidence, ...]
    settings: tuple[ObservedSetting, ...]
    integrations: tuple[IntegrationObservation, ...]
    mathematical_models: MathematicalModelCatalog
    warnings: tuple[RecipeWarning, ...]
    execution_authorized: bool = False
    recipe_id: str = field(init=False)

    def __post_init__(self) -> None:
        if _NAME.fullmatch(self.engine_name) is None:
            raise ValueError("engine_name is invalid")
        if _NAME.fullmatch(self.source_component) is None:
            raise ValueError("source_component is invalid")
        if (
            not self.source_repository_url.startswith("https://")
            or len(self.source_repository_url) > 2_048
            or any(character.isspace() for character in self.source_repository_url)
        ):
            raise ValueError("source_repository_url must be a bounded HTTPS URL")
        if _GIT_SHA1.fullmatch(self.source_revision) is None:
            raise ValueError("source_revision must be an exact Git SHA-1 commit")
        if _GIT_SHA1.fullmatch(self.source_tree) is None:
            raise ValueError("source_tree must be an exact Git SHA-1 tree")
        _relative_path(self.source_example_root, "source_example_root")
        _relative_path(self.source_license_path, "source_license_path")
        if _SHA256.fullmatch(self.source_license_sha256) is None:
            raise ValueError("source_license_sha256 is invalid")
        if not self.source_files or len(self.source_files) > 10_000:
            raise ValueError("source file evidence is invalid")
        paths = tuple(item.relative_path for item in self.source_files)
        if paths != tuple(sorted(paths)) or len(paths) != len(set(paths)):
            raise ValueError("source files must have unique sorted paths")
        if len(self.settings) > 10_000:
            raise ValueError("too many observed settings")
        if not self.integrations:
            raise ValueError("at least one integration observation is required")
        from projectkoios.frankensteins.mathematics.models import (
            MathematicalModelCatalog,
        )

        if not isinstance(self.mathematical_models, MathematicalModelCatalog):
            raise TypeError("mathematical_models must be a MathematicalModelCatalog")
        if (
            self.mathematical_models.source_component != self.source_component
            or self.mathematical_models.source_revision != self.source_revision
            or self.mathematical_models.source_example_root != self.source_example_root
        ):
            raise ValueError(
                "mathematical-model provenance must match recipe provenance"
            )
        if self.execution_authorized:
            raise ValueError("a reconstructed recipe cannot authorize execution")
        identity = stable_id("frankenstein-recipe", self._identity_dict())
        object.__setattr__(self, "recipe_id", identity)

    def _identity_dict(self) -> dict[str, object]:
        return {
            "contract": "projectkoios.frankenstein-recipe",
            "contract_version": "0.3.0",
            "engine_name": self.engine_name,
            "source_component": self.source_component,
            "source_repository_url": self.source_repository_url,
            "source_revision": self.source_revision,
            "source_tree": self.source_tree,
            "source_example_root": self.source_example_root,
            "source_license_path": self.source_license_path,
            "source_license_sha256": self.source_license_sha256,
            "source_files": [item.to_dict() for item in self.source_files],
            "settings": [item.to_dict() for item in self.settings],
            "integrations": [item.to_dict() for item in self.integrations],
            "mathematical_models": self.mathematical_models.to_dict(),
            "warnings": [item.to_dict() for item in self.warnings],
            "execution_authorized": self.execution_authorized,
        }

    def to_dict(self) -> dict[str, object]:
        return {**self._identity_dict(), "recipe_id": self.recipe_id}

    def to_json(self) -> str:
        return (
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)
            + "\n"
        )


def json_payload(value: dict[str, Any]) -> str:
    """Return canonical JSON for an integration observation."""
    return canonical_json_bytes(value).decode("utf-8")
