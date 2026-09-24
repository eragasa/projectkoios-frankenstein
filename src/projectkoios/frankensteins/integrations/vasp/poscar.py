from __future__ import annotations

import math
from dataclasses import dataclass

from projectkoios.frankensteins.core import SourceFileEvidence


@dataclass(frozen=True)
class VaspStructureObservation:
    name: str
    evidence: SourceFileEvidence
    comment: str
    scale: str
    element_symbols: tuple[str, ...]
    element_counts: tuple[int, ...]
    coordinate_mode: str
    coordinate_count: int

    def __post_init__(self) -> None:
        if not self.name or len(self.name) > 128:
            raise ValueError("VASP structure name is invalid")
        if not self.comment or len(self.comment) > 512:
            raise ValueError("VASP comment is invalid")
        try:
            scale = float(self.scale)
        except ValueError as error:
            raise ValueError("VASP scale is invalid") from error
        if not math.isfinite(scale) or scale == 0:
            raise ValueError("VASP scale must be finite and nonzero")
        if self.element_symbols and len(self.element_symbols) != len(
            self.element_counts
        ):
            raise ValueError("VASP element symbols and counts do not align")
        if not self.element_counts or any(value <= 0 for value in self.element_counts):
            raise ValueError("VASP element counts are invalid")
        if self.coordinate_mode not in {"direct", "cartesian"}:
            raise ValueError("VASP coordinate mode is unsupported")
        if self.coordinate_count != sum(self.element_counts):
            raise ValueError("VASP coordinate count does not match element counts")

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "evidence": self.evidence.to_dict(),
            "comment": self.comment,
            "scale": self.scale,
            "element_symbols": list(self.element_symbols),
            "element_counts": list(self.element_counts),
            "coordinate_mode": self.coordinate_mode,
            "coordinate_count": self.coordinate_count,
            "calculator_execution_authorized": False,
            "scientific_validity_claimed": False,
        }


def inspect_poscar(
    *,
    name: str,
    evidence: SourceFileEvidence,
    text: str,
) -> VaspStructureObservation:
    if len(text.encode("utf-8")) > 10_000_000:
        raise ValueError("VASP structure exceeds inspection byte limit")
    lines = [line.strip() for line in text.splitlines()]
    if len(lines) < 8:
        raise ValueError("VASP structure is incomplete")
    comment = lines[0]
    scale = lines[1]
    for index in range(2, 5):
        _three_finite_floats(lines[index], "VASP lattice vector")

    fifth = lines[5].split()
    if not fifth:
        raise ValueError("VASP element line is empty")
    if all(token.isdigit() for token in fifth):
        symbols: tuple[str, ...] = ()
        counts = tuple(int(token) for token in fifth)
        cursor = 6
    else:
        symbols = tuple(fifth)
        count_tokens = lines[6].split()
        if not count_tokens or not all(token.isdigit() for token in count_tokens):
            raise ValueError("VASP element-count line is invalid")
        counts = tuple(int(token) for token in count_tokens)
        cursor = 7

    if cursor >= len(lines):
        raise ValueError("VASP coordinate mode is missing")
    if lines[cursor].casefold().startswith("s"):
        cursor += 1
    if cursor >= len(lines):
        raise ValueError("VASP coordinate mode is missing")
    mode_token = lines[cursor].casefold()
    if mode_token.startswith("d"):
        mode = "direct"
    elif mode_token.startswith("c") or mode_token.startswith("k"):
        mode = "cartesian"
    else:
        raise ValueError("VASP coordinate mode is unsupported")
    cursor += 1

    coordinate_count = sum(counts)
    if len(lines) < cursor + coordinate_count:
        raise ValueError("VASP coordinate rows are incomplete")
    for line in lines[cursor : cursor + coordinate_count]:
        tokens = line.split()
        if len(tokens) < 3:
            raise ValueError("VASP coordinate row is incomplete")
        _three_finite_floats(" ".join(tokens[:3]), "VASP coordinate")

    return VaspStructureObservation(
        name=name,
        evidence=evidence,
        comment=comment,
        scale=scale,
        element_symbols=symbols,
        element_counts=counts,
        coordinate_mode=mode,
        coordinate_count=coordinate_count,
    )


def _three_finite_floats(value: str, label: str) -> None:
    tokens = value.split()
    if len(tokens) != 3:
        raise ValueError(f"{label} must contain three values")
    try:
        numbers = tuple(float(token) for token in tokens)
    except ValueError as error:
        raise ValueError(f"{label} contains a nonnumeric value") from error
    if not all(math.isfinite(number) for number in numbers):
        raise ValueError(f"{label} contains a nonfinite value")
