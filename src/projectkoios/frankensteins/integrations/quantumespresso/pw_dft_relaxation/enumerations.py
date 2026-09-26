"""QE 7.5 relaxation enumerations with reviewed native descriptions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

QE_INPUT_PW_VERSION = "7.5"
QE_INPUT_PW_AUTHORITY = "https://www.quantum-espresso.org/Doc/INPUT_PW.html"


class QeRelaxationCalculation(StrEnum):
    """Represent structural-relaxation values of ``&CONTROL.calculation``."""

    RELAX = "relax"
    VC_RELAX = "vc-relax"


class QeRelaxationIonDynamics(StrEnum):
    """Represent ``&IONS.ion_dynamics`` values used for relaxation."""

    BFGS = "bfgs"
    DAMP = "damp"
    FIRE = "fire"


class QeRelaxationCellDynamics(StrEnum):
    """Represent documented ``vc-relax`` values of ``&CELL.cell_dynamics``."""

    NONE = "none"
    STEEPEST_DESCENT = "sd"
    DAMPED_PARRINELLO_RAHMAN = "damp-pr"
    DAMPED_WENTZCOVITCH = "damp-w"
    BFGS = "bfgs"


class QeRelaxationCellDegreesOfFreedom(StrEnum):
    """Represent documented base values of ``&CELL.cell_dofree``."""

    ALL = "all"
    IBRAV = "ibrav"
    A = "a"
    B = "b"
    C = "c"
    FIX_A = "fixa"
    FIX_B = "fixb"
    FIX_C = "fixc"
    X = "x"
    Y = "y"
    Z = "z"
    XY = "xy"
    XZ = "xz"
    YZ = "yz"
    XYZ = "xyz"
    SHAPE = "shape"
    VOLUME = "volume"
    TWO_DIMENSIONAL_XY = "2Dxy"
    TWO_DIMENSIONAL_SHAPE = "2Dshape"
    EPITAXIAL_AB = "epitaxial_ab"
    EPITAXIAL_AC = "epitaxial_ac"
    EPITAXIAL_BC = "epitaxial_bc"


class QeNativeValueStatus(StrEnum):
    """State whether Project Koios may project one documented native value."""

    SUPPORTED = "supported"
    DOCUMENTED_NOT_IMPLEMENTED_BY_QE = "documented-not-implemented-by-qe"


QeRelaxationNativeValue = (
    QeRelaxationCalculation
    | QeRelaxationIonDynamics
    | QeRelaxationCellDynamics
    | QeRelaxationCellDegreesOfFreedom
)


@dataclass(frozen=True, slots=True)
class QeRelaxationEnumDescription:
    """Describe one native enum value and its valid relaxation context."""

    value: QeRelaxationNativeValue
    variable: str
    purpose: str
    allowed_calculations: tuple[QeRelaxationCalculation, ...]
    required_companion_fields: tuple[str, ...]
    status: QeNativeValueStatus
    qualification: str
    authority_url: str = QE_INPUT_PW_AUTHORITY
    authority_version: str = QE_INPUT_PW_VERSION

    def __post_init__(self) -> None:
        if not isinstance(
            self.value,
            (
                QeRelaxationCalculation,
                QeRelaxationIonDynamics,
                QeRelaxationCellDynamics,
                QeRelaxationCellDegreesOfFreedom,
            ),
        ):
            raise TypeError("value must be a QE relaxation enum")
        for label, text in (
            ("variable", self.variable),
            ("purpose", self.purpose),
            ("qualification", self.qualification),
            ("authority_url", self.authority_url),
            ("authority_version", self.authority_version),
        ):
            if type(text) is not str or not text or text != text.strip():
                raise ValueError(f"{label} must be nonempty and stripped")
        if not self.allowed_calculations or any(
            type(item) is not QeRelaxationCalculation
            for item in self.allowed_calculations
        ):
            raise TypeError(
                "allowed_calculations must contain QeRelaxationCalculation values"
            )
        if type(self.required_companion_fields) is not tuple or any(
            type(item) is not str or not item for item in self.required_companion_fields
        ):
            raise TypeError("required_companion_fields must contain strings")
        if type(self.status) is not QeNativeValueStatus:
            raise TypeError("status must be a QeNativeValueStatus")


_BOTH = (QeRelaxationCalculation.RELAX, QeRelaxationCalculation.VC_RELAX)
_VC = (QeRelaxationCalculation.VC_RELAX,)

QE_RELAXATION_ENUM_DESCRIPTIONS = (
    QeRelaxationEnumDescription(
        value=QeRelaxationCalculation.RELAX,
        variable="&CONTROL.calculation",
        purpose="Relax atomic positions with a fixed simulation cell.",
        allowed_calculations=(QeRelaxationCalculation.RELAX,),
        required_companion_fields=("&IONS.ion_dynamics",),
        status=QeNativeValueStatus.SUPPORTED,
        qualification="This value does not request cell dynamics.",
    ),
    QeRelaxationEnumDescription(
        value=QeRelaxationCalculation.VC_RELAX,
        variable="&CONTROL.calculation",
        purpose="Relax atomic positions and declared cell degrees of freedom.",
        allowed_calculations=(QeRelaxationCalculation.VC_RELAX,),
        required_companion_fields=(
            "&IONS.ion_dynamics",
            "&CELL.cell_dynamics",
            "&CELL.cell_dofree",
        ),
        status=QeNativeValueStatus.SUPPORTED,
        qualification="Pressure and cell convergence controls remain explicit.",
    ),
    QeRelaxationEnumDescription(
        value=QeRelaxationIonDynamics.BFGS,
        variable="&IONS.ion_dynamics",
        purpose="Use QE's trust-radius BFGS quasi-Newton ionic optimizer.",
        allowed_calculations=_BOTH,
        required_companion_fields=("&CELL.cell_dynamics='bfgs' for vc-relax",),
        status=QeNativeValueStatus.SUPPORTED,
        qualification="BFGS does not imply equivalence to another code's optimizer.",
    ),
    QeRelaxationEnumDescription(
        value=QeRelaxationIonDynamics.DAMP,
        variable="&IONS.ion_dynamics",
        purpose="Use QE damped dynamics for structural relaxation.",
        allowed_calculations=_BOTH,
        required_companion_fields=("compatible &CELL.cell_dynamics for vc-relax",),
        status=QeNativeValueStatus.SUPPORTED,
        qualification="The relax and vc-relax implementations use different schemes.",
    ),
    QeRelaxationEnumDescription(
        value=QeRelaxationIonDynamics.FIRE,
        variable="&IONS.ion_dynamics",
        purpose="Use QE's FIRE minimization implementation.",
        allowed_calculations=(QeRelaxationCalculation.RELAX,),
        required_companion_fields=(),
        status=QeNativeValueStatus.SUPPORTED,
        qualification="QE 7.5 documents FIRE for fixed-cell relax calculations.",
    ),
    QeRelaxationEnumDescription(
        value=QeRelaxationCellDynamics.NONE,
        variable="&CELL.cell_dynamics",
        purpose="Disable cell dynamics.",
        allowed_calculations=_VC,
        required_companion_fields=(),
        status=QeNativeValueStatus.SUPPORTED,
        qualification=(
            "This documented value does not satisfy a generic request to relax "
            "the cell."
        ),
    ),
    QeRelaxationEnumDescription(
        value=QeRelaxationCellDynamics.STEEPEST_DESCENT,
        variable="&CELL.cell_dynamics",
        purpose="Request the documented steepest-descent cell mode.",
        allowed_calculations=_VC,
        required_companion_fields=(),
        status=QeNativeValueStatus.DOCUMENTED_NOT_IMPLEMENTED_BY_QE,
        qualification="QE 7.5 INPUT_PW marks this value as not implemented.",
    ),
    QeRelaxationEnumDescription(
        value=QeRelaxationCellDynamics.DAMPED_PARRINELLO_RAHMAN,
        variable="&CELL.cell_dynamics",
        purpose="Use damped Beeman Parrinello-Rahman cell dynamics.",
        allowed_calculations=_VC,
        required_companion_fields=("&IONS.ion_dynamics='damp'",),
        status=QeNativeValueStatus.SUPPORTED,
        qualification="This is a QE-native cell algorithm, not a cross-code synonym.",
    ),
    QeRelaxationEnumDescription(
        value=QeRelaxationCellDynamics.DAMPED_WENTZCOVITCH,
        variable="&CELL.cell_dynamics",
        purpose="Use damped Beeman Wentzcovitch cell dynamics.",
        allowed_calculations=_VC,
        required_companion_fields=("&IONS.ion_dynamics='damp'",),
        status=QeNativeValueStatus.SUPPORTED,
        qualification="This is a QE-native cell algorithm, not a cross-code synonym.",
    ),
    QeRelaxationEnumDescription(
        value=QeRelaxationCellDynamics.BFGS,
        variable="&CELL.cell_dynamics",
        purpose="Use QE's BFGS quasi-Newton cell optimizer.",
        allowed_calculations=_VC,
        required_companion_fields=("&IONS.ion_dynamics='bfgs'",),
        status=QeNativeValueStatus.SUPPORTED,
        qualification="QE requires BFGS ionic dynamics for this cell mode.",
    ),
    *(
        QeRelaxationEnumDescription(
            value=value,
            variable="&CELL.cell_dofree",
            purpose=purpose,
            allowed_calculations=_VC,
            required_companion_fields=("&CELL.cell_dynamics",),
            status=QeNativeValueStatus.SUPPORTED,
            qualification=qualification,
        )
        for value, purpose, qualification in (
            (
                QeRelaxationCellDegreesOfFreedom.ALL,
                "Move all cell axes and angles.",
                "The lattice is not constrained to its initial Bravais family.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.IBRAV,
                "Move the cell while retaining an ibrav-consistent lattice.",
                "This base value is incompatible with the maintained ibrav=0 "
                "projection.",
            ),
            (QeRelaxationCellDegreesOfFreedom.A, "Fix v1_x.", "QE native semantics."),
            (QeRelaxationCellDegreesOfFreedom.B, "Fix v2_y.", "QE native semantics."),
            (QeRelaxationCellDegreesOfFreedom.C, "Fix v3_z.", "QE native semantics."),
            (
                QeRelaxationCellDegreesOfFreedom.FIX_A,
                "Fix axis 1.",
                "QE native semantics.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.FIX_B,
                "Fix axis 2.",
                "QE native semantics.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.FIX_C,
                "Fix axis 3.",
                "QE native semantics.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.X,
                "Move only v1_x.",
                "QE native semantics.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.Y,
                "Move only v2_y.",
                "QE native semantics.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.Z,
                "Move only v3_z.",
                "QE native semantics.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.XY,
                "Move v1_x and v2_y.",
                "QE native semantics.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.XZ,
                "Move v1_x and v3_z.",
                "QE native semantics.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.YZ,
                "Move v2_y and v3_z.",
                "QE native semantics.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.XYZ,
                "Move v1_x, v2_y, and v3_z.",
                "Angles remain fixed under QE's native interpretation.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.SHAPE,
                "Move axes and angles at fixed volume.",
                "Volume remains constrained by QE.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.VOLUME,
                "Change volume while retaining angles.",
                "QE implements this through its native cell representation.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.TWO_DIMENSIONAL_XY,
                "Move only x and y cell components.",
                "Intended for QE two-dimensional cell control.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.TWO_DIMENSIONAL_SHAPE,
                "Move x and y components at fixed in-plane area.",
                "Intended for QE two-dimensional cell control.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.EPITAXIAL_AB,
                "Fix axes 1 and 2 while moving axis 3.",
                "QE native epitaxial constraint.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.EPITAXIAL_AC,
                "Fix axes 1 and 3 while moving axis 2.",
                "QE native epitaxial constraint.",
            ),
            (
                QeRelaxationCellDegreesOfFreedom.EPITAXIAL_BC,
                "Fix axes 2 and 3 while moving axis 1.",
                "QE native epitaxial constraint.",
            ),
        )
    ),
)
