"""Nominal Quantum ESPRESSO namelist and data-card records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Literal

from projectkoios.frankensteins.io.quantumespresso.input import PwInputGroup


@dataclass(frozen=True, slots=True)
class QeCard:
    """Represent one ordered QE namelist or data card."""

    lines: tuple[str, ...]
    option: str | None = None

    _kind: ClassVar[Literal["namelist", "card"]]
    _tag: ClassVar[str]

    def __post_init__(self) -> None:
        if type(self) is QeCard:
            raise TypeError("QeCard is a nominal base and cannot be instantiated")
        if self._kind not in {"namelist", "card"}:
            raise TypeError("QeCard subclass must declare a supported kind")
        if not self._tag:
            raise TypeError("QeCard subclass must declare a tag")
        if type(self.lines) is not tuple:
            raise TypeError("lines must be a tuple")
        for line in self.lines:
            if type(line) is not str:
                raise TypeError("lines must contain strings")
            if line != line.strip() or "\n" in line or "\r" in line:
                raise ValueError(
                    "lines must be stripped and contain no line terminators"
                )
        if self.option is not None:
            if type(self.option) is not str:
                raise TypeError("option must be a string or None")
            if (
                not self.option
                or self.option != self.option.strip()
                or "\n" in self.option
                or "\r" in self.option
            ):
                raise ValueError(
                    "option must be nonempty, stripped, and contain no line terminators"
                )
            if self._kind == "namelist":
                raise ValueError("QE namelists do not accept card options")

    @property
    def kind(self) -> Literal["namelist", "card"]:
        """Return whether this record is a namelist or data card."""
        return self._kind

    @property
    def tag(self) -> str:
        """Return the rendered group tag, including an optional card option."""
        if self.option is None:
            return self._tag
        return f"{self._tag} {self.option}"

    def to_input_group(self) -> PwInputGroup:
        """Project this nominal record into the maintained lexical group model."""
        return PwInputGroup(kind=self.kind, tag=self.tag, lines=self.lines)


class QeControlCard(QeCard):
    """Represent the required ``&CONTROL`` namelist."""

    __slots__ = ()

    _kind = "namelist"
    _tag = "&CONTROL"


class QeSystemCard(QeCard):
    """Represent the required ``&SYSTEM`` namelist."""

    __slots__ = ()

    _kind = "namelist"
    _tag = "&SYSTEM"


class QeElectronsCard(QeCard):
    """Represent the required ``&ELECTRONS`` namelist."""

    __slots__ = ()

    _kind = "namelist"
    _tag = "&ELECTRONS"


class QeIonsCard(QeCard):
    """Represent the optional ``&IONS`` namelist."""

    __slots__ = ()

    _kind = "namelist"
    _tag = "&IONS"


class QeCellCard(QeCard):
    """Represent the optional ``&CELL`` namelist."""

    __slots__ = ()

    _kind = "namelist"
    _tag = "&CELL"


class QeFcpCard(QeCard):
    """Represent the optional ``&FCP`` namelist."""

    __slots__ = ()

    _kind = "namelist"
    _tag = "&FCP"


class QeRismCard(QeCard):
    """Represent the optional ``&RISM`` namelist."""

    __slots__ = ()

    _kind = "namelist"
    _tag = "&RISM"


class QeAtomicSpeciesCard(QeCard):
    """Represent an ``ATOMIC_SPECIES`` data card."""

    __slots__ = ()

    _kind = "card"
    _tag = "ATOMIC_SPECIES"


class QeAtomicPositionsCard(QeCard):
    """Represent an ``ATOMIC_POSITIONS`` data card."""

    __slots__ = ()

    _kind = "card"
    _tag = "ATOMIC_POSITIONS"


class QeKpointsCard(QeCard):
    """Represent a ``K_POINTS`` data card."""

    __slots__ = ()

    _kind = "card"
    _tag = "K_POINTS"


class QeAdditionalKpointsCard(QeCard):
    """Represent an ``ADDITIONAL_K_POINTS`` data card."""

    __slots__ = ()

    _kind = "card"
    _tag = "ADDITIONAL_K_POINTS"


class QeCellParametersCard(QeCard):
    """Represent a ``CELL_PARAMETERS`` data card."""

    __slots__ = ()

    _kind = "card"
    _tag = "CELL_PARAMETERS"


class QeOccupationsCard(QeCard):
    """Represent an ``OCCUPATIONS`` data card."""

    __slots__ = ()

    _kind = "card"
    _tag = "OCCUPATIONS"


class QeConstraintsCard(QeCard):
    """Represent a ``CONSTRAINTS`` data card."""

    __slots__ = ()

    _kind = "card"
    _tag = "CONSTRAINTS"


class QeAtomicVelocitiesCard(QeCard):
    """Represent an ``ATOMIC_VELOCITIES`` data card."""

    __slots__ = ()

    _kind = "card"
    _tag = "ATOMIC_VELOCITIES"


class QeAtomicForcesCard(QeCard):
    """Represent an ``ATOMIC_FORCES`` data card."""

    __slots__ = ()

    _kind = "card"
    _tag = "ATOMIC_FORCES"


class QeSolventsCard(QeCard):
    """Represent a ``SOLVENTS`` data card."""

    __slots__ = ()

    _kind = "card"
    _tag = "SOLVENTS"


class QeHubbardCard(QeCard):
    """Represent a ``HUBBARD`` data card."""

    __slots__ = ()

    _kind = "card"
    _tag = "HUBBARD"
