"""Dimensionless three-dimensional Bravais direct lattices."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

import numpy as np

from physkit.periodic import DirectLattice3D


class BravaisLatticeKind(StrEnum):
    """Identify a three-dimensional Bravais-lattice vector convention."""

    free = "free"
    cubic_primitive = "cubic_primitive"
    cubic_face_centered = "cubic_face_centered"
    cubic_body_centered = "cubic_body_centered"
    cubic_body_centered_symmetric = "cubic_body_centered_symmetric"
    hexagonal_trigonal_primitive = "hexagonal_trigonal_primitive"
    trigonal_rhombohedral_axis_c = "trigonal_rhombohedral_axis_c"
    trigonal_rhombohedral_axis_111 = "trigonal_rhombohedral_axis_111"
    tetragonal_primitive = "tetragonal_primitive"
    tetragonal_body_centered = "tetragonal_body_centered"
    orthorhombic_primitive = "orthorhombic_primitive"
    orthorhombic_base_centered = "orthorhombic_base_centered"
    orthorhombic_base_centered_alternate = "orthorhombic_base_centered_alternate"
    orthorhombic_one_face_base_centered = "orthorhombic_one_face_base_centered"
    orthorhombic_face_centered = "orthorhombic_face_centered"
    orthorhombic_body_centered = "orthorhombic_body_centered"
    monoclinic_primitive_unique_c = "monoclinic_primitive_unique_c"
    monoclinic_primitive_unique_b = "monoclinic_primitive_unique_b"
    monoclinic_base_centered_unique_c = "monoclinic_base_centered_unique_c"
    monoclinic_base_centered_unique_b = "monoclinic_base_centered_unique_b"
    triclinic = "triclinic"


@dataclass(frozen=True, slots=True)
class BravaisLattice:
    """Bind a named convention to a dimensionless direct-lattice matrix ``A``."""

    kind: BravaisLatticeKind
    direct_lattice: DirectLattice3D

    def __post_init__(self) -> None:
        if type(self.kind) is not BravaisLatticeKind:
            raise TypeError("kind must be a BravaisLatticeKind")
        if not isinstance(self.direct_lattice, DirectLattice3D):
            raise TypeError("direct_lattice must be a DirectLattice3D")

    @classmethod
    def free(cls, direct_lattice: DirectLattice3D) -> BravaisLattice:
        """Retain caller-supplied dimensionless direct-lattice vectors."""
        return cls(BravaisLatticeKind.free, direct_lattice)

    @classmethod
    def cubic_primitive(cls) -> BravaisLattice:
        """Construct primitive cubic vectors."""
        return cls._from_rows(
            BravaisLatticeKind.cubic_primitive,
            ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        )

    @classmethod
    def cubic_face_centered(cls) -> BravaisLattice:
        """Construct face-centered cubic vectors."""
        return cls._from_rows(
            BravaisLatticeKind.cubic_face_centered,
            ((-0.5, 0.0, 0.5), (0.0, 0.5, 0.5), (-0.5, 0.5, 0.0)),
        )

    @classmethod
    def cubic_body_centered(cls) -> BravaisLattice:
        """Construct body-centered cubic vectors."""
        return cls._from_rows(
            BravaisLatticeKind.cubic_body_centered,
            ((0.5, 0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5)),
        )

    @classmethod
    def cubic_body_centered_symmetric(cls) -> BravaisLattice:
        """Construct the symmetric-axis body-centered cubic convention."""
        return cls._from_rows(
            BravaisLatticeKind.cubic_body_centered_symmetric,
            ((-0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, -0.5)),
        )

    @classmethod
    def hexagonal_trigonal_primitive(cls, c_over_a: float) -> BravaisLattice:
        """Construct primitive hexagonal or trigonal vectors."""
        c = _positive_ratio(c_over_a, "c_over_a")
        return cls._from_rows(
            BravaisLatticeKind.hexagonal_trigonal_primitive,
            (
                (1.0, 0.0, 0.0),
                (-0.5, math.sqrt(3.0) / 2.0, 0.0),
                (0.0, 0.0, c),
            ),
        )

    @classmethod
    def trigonal_rhombohedral_axis_c(cls, cos_gamma: float) -> BravaisLattice:
        """Construct rhombohedral vectors around the Cartesian c axis."""
        tx, ty, tz = _rhombohedral_components(cos_gamma)
        return cls._from_rows(
            BravaisLatticeKind.trigonal_rhombohedral_axis_c,
            ((tx, -ty, tz), (0.0, 2.0 * ty, tz), (-tx, -ty, tz)),
        )

    @classmethod
    def trigonal_rhombohedral_axis_111(cls, cos_gamma: float) -> BravaisLattice:
        """Construct rhombohedral vectors around the Cartesian <111> axis."""
        _, ty, tz = _rhombohedral_components(cos_gamma)
        u = tz - 2.0 * math.sqrt(2.0) * ty
        v = tz + math.sqrt(2.0) * ty
        scale = 1.0 / math.sqrt(3.0)
        return cls._from_rows(
            BravaisLatticeKind.trigonal_rhombohedral_axis_111,
            (
                (scale * u, scale * v, scale * v),
                (scale * v, scale * u, scale * v),
                (scale * v, scale * v, scale * u),
            ),
        )

    @classmethod
    def tetragonal_primitive(cls, c_over_a: float) -> BravaisLattice:
        """Construct primitive tetragonal vectors."""
        c = _positive_ratio(c_over_a, "c_over_a")
        return cls._from_rows(
            BravaisLatticeKind.tetragonal_primitive,
            ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, c)),
        )

    @classmethod
    def tetragonal_body_centered(cls, c_over_a: float) -> BravaisLattice:
        """Construct body-centered tetragonal vectors."""
        half_c = _positive_ratio(c_over_a, "c_over_a") / 2.0
        return cls._from_rows(
            BravaisLatticeKind.tetragonal_body_centered,
            ((0.5, -0.5, half_c), (0.5, 0.5, half_c), (-0.5, -0.5, half_c)),
        )

    @classmethod
    def orthorhombic_primitive(cls, b_over_a: float, c_over_a: float) -> BravaisLattice:
        """Construct primitive orthorhombic vectors."""
        b, c = _orthorhombic_ratios(b_over_a, c_over_a)
        return cls._from_rows(
            BravaisLatticeKind.orthorhombic_primitive,
            ((1.0, 0.0, 0.0), (0.0, b, 0.0), (0.0, 0.0, c)),
        )

    @classmethod
    def orthorhombic_base_centered(
        cls, b_over_a: float, c_over_a: float
    ) -> BravaisLattice:
        """Construct base-centered orthorhombic vectors."""
        b, c = _orthorhombic_ratios(b_over_a, c_over_a)
        return cls._from_rows(
            BravaisLatticeKind.orthorhombic_base_centered,
            ((0.5, b / 2.0, 0.0), (-0.5, b / 2.0, 0.0), (0.0, 0.0, c)),
        )

    @classmethod
    def orthorhombic_base_centered_alternate(
        cls, b_over_a: float, c_over_a: float
    ) -> BravaisLattice:
        """Construct the alternate base-centered orthorhombic convention."""
        b, c = _orthorhombic_ratios(b_over_a, c_over_a)
        return cls._from_rows(
            BravaisLatticeKind.orthorhombic_base_centered_alternate,
            ((0.5, -b / 2.0, 0.0), (0.5, b / 2.0, 0.0), (0.0, 0.0, c)),
        )

    @classmethod
    def orthorhombic_one_face_base_centered(
        cls, b_over_a: float, c_over_a: float
    ) -> BravaisLattice:
        """Construct one-face base-centered A-type orthorhombic vectors."""
        b, c = _orthorhombic_ratios(b_over_a, c_over_a)
        return cls._from_rows(
            BravaisLatticeKind.orthorhombic_one_face_base_centered,
            ((1.0, 0.0, 0.0), (0.0, b / 2.0, -c / 2.0), (0.0, b / 2.0, c / 2.0)),
        )

    @classmethod
    def orthorhombic_face_centered(
        cls, b_over_a: float, c_over_a: float
    ) -> BravaisLattice:
        """Construct face-centered orthorhombic vectors."""
        b, c = _orthorhombic_ratios(b_over_a, c_over_a)
        return cls._from_rows(
            BravaisLatticeKind.orthorhombic_face_centered,
            ((0.5, 0.0, c / 2.0), (0.5, b / 2.0, 0.0), (0.0, b / 2.0, c / 2.0)),
        )

    @classmethod
    def orthorhombic_body_centered(
        cls, b_over_a: float, c_over_a: float
    ) -> BravaisLattice:
        """Construct body-centered orthorhombic vectors."""
        b, c = _orthorhombic_ratios(b_over_a, c_over_a)
        return cls._from_rows(
            BravaisLatticeKind.orthorhombic_body_centered,
            (
                (0.5, b / 2.0, c / 2.0),
                (-0.5, b / 2.0, c / 2.0),
                (-0.5, -b / 2.0, c / 2.0),
            ),
        )

    @classmethod
    def monoclinic_primitive_unique_c(
        cls, b_over_a: float, c_over_a: float, cos_ab: float
    ) -> BravaisLattice:
        """Construct primitive monoclinic vectors with unique axis c."""
        b, c = _orthorhombic_ratios(b_over_a, c_over_a)
        cosine, sine = _cosine_and_sine(cos_ab, "cos_ab")
        return cls._from_rows(
            BravaisLatticeKind.monoclinic_primitive_unique_c,
            ((1.0, 0.0, 0.0), (b * cosine, b * sine, 0.0), (0.0, 0.0, c)),
        )

    @classmethod
    def monoclinic_primitive_unique_b(
        cls, b_over_a: float, c_over_a: float, cos_ac: float
    ) -> BravaisLattice:
        """Construct primitive monoclinic vectors with unique axis b."""
        b, c = _orthorhombic_ratios(b_over_a, c_over_a)
        cosine, sine = _cosine_and_sine(cos_ac, "cos_ac")
        return cls._from_rows(
            BravaisLatticeKind.monoclinic_primitive_unique_b,
            ((1.0, 0.0, 0.0), (0.0, b, 0.0), (c * cosine, 0.0, c * sine)),
        )

    @classmethod
    def monoclinic_base_centered_unique_c(
        cls, b_over_a: float, c_over_a: float, cos_ab: float
    ) -> BravaisLattice:
        """Construct base-centered monoclinic vectors with unique axis c."""
        b, c = _orthorhombic_ratios(b_over_a, c_over_a)
        cosine, sine = _cosine_and_sine(cos_ab, "cos_ab")
        return cls._from_rows(
            BravaisLatticeKind.monoclinic_base_centered_unique_c,
            (
                (0.5, 0.0, -c / 2.0),
                (b * cosine, b * sine, 0.0),
                (0.5, 0.0, c / 2.0),
            ),
        )

    @classmethod
    def monoclinic_base_centered_unique_b(
        cls, b_over_a: float, c_over_a: float, cos_ac: float
    ) -> BravaisLattice:
        """Construct base-centered monoclinic vectors with unique axis b."""
        b, c = _orthorhombic_ratios(b_over_a, c_over_a)
        cosine, sine = _cosine_and_sine(cos_ac, "cos_ac")
        return cls._from_rows(
            BravaisLatticeKind.monoclinic_base_centered_unique_b,
            (
                (0.5, b / 2.0, 0.0),
                (-0.5, b / 2.0, 0.0),
                (c * cosine, 0.0, c * sine),
            ),
        )

    @classmethod
    def triclinic(
        cls,
        b_over_a: float,
        c_over_a: float,
        cos_bc: float,
        cos_ac: float,
        cos_ab: float,
    ) -> BravaisLattice:
        """Construct triclinic vectors from length ratios and angle cosines."""
        b, c = _orthorhombic_ratios(b_over_a, c_over_a)
        alpha = _cosine(cos_bc, "cos_bc")
        beta = _cosine(cos_ac, "cos_ac")
        gamma, sin_gamma = _cosine_and_sine(cos_ab, "cos_ab")
        volume_term = (
            1.0
            + 2.0 * alpha * beta * gamma
            - alpha * alpha
            - beta * beta
            - gamma * gamma
        )
        if volume_term <= 0.0:
            raise ValueError("triclinic angle cosines must define positive volume")
        return cls._from_rows(
            BravaisLatticeKind.triclinic,
            (
                (1.0, 0.0, 0.0),
                (b * gamma, b * sin_gamma, 0.0),
                (
                    c * beta,
                    c * (alpha - beta * gamma) / sin_gamma,
                    c * math.sqrt(volume_term) / sin_gamma,
                ),
            ),
        )

    @classmethod
    def _from_rows(
        cls,
        kind: BravaisLatticeKind,
        rows: tuple[
            tuple[float, float, float],
            tuple[float, float, float],
            tuple[float, float, float],
        ],
    ) -> BravaisLattice:
        return cls(
            kind=kind,
            direct_lattice=DirectLattice3D(
                a1=np.asarray(rows[0], dtype=np.float64),
                a2=np.asarray(rows[1], dtype=np.float64),
                a3=np.asarray(rows[2], dtype=np.float64),
            ),
        )


def _positive_ratio(value: float, label: str) -> float:
    if type(value) is not float or not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{label} must be a positive finite float")
    return value


def _orthorhombic_ratios(b_over_a: float, c_over_a: float) -> tuple[float, float]:
    return (
        _positive_ratio(b_over_a, "b_over_a"),
        _positive_ratio(c_over_a, "c_over_a"),
    )


def _cosine(value: float, label: str) -> float:
    if type(value) is not float or not math.isfinite(value) or not -1.0 < value < 1.0:
        raise ValueError(f"{label} must be a finite float strictly between -1 and 1")
    return value


def _cosine_and_sine(value: float, label: str) -> tuple[float, float]:
    cosine = _cosine(value, label)
    return cosine, math.sqrt(1.0 - cosine * cosine)


def _rhombohedral_components(cos_gamma: float) -> tuple[float, float, float]:
    cosine = _cosine(cos_gamma, "cos_gamma")
    if cosine <= -0.5:
        raise ValueError("cos_gamma must be greater than -0.5")
    return (
        math.sqrt((1.0 - cosine) / 2.0),
        math.sqrt((1.0 - cosine) / 6.0),
        math.sqrt((1.0 + 2.0 * cosine) / 3.0),
    )
