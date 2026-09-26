"""Project generic relaxation intent into typed QE namelists and data cards."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from physkit.units import MODEL_SYSTEM_UNIT_CONVERTER, PhysicalUnit

from projectkoios.frankensteins.applications.calculator import (
    CalculatorIntegrationId,
)
from projectkoios.frankensteins.applications.pw_dft_relaxation.base import (
    PwDftRelaxationRequest,
    PwDftRelaxationScope,
)
from projectkoios.frankensteins.applications.pw_dft_relaxation.integration import (
    PwDftRelaxationInputProjection,
    PwDftRelaxationRenderedInput,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_relaxation import (
    configuration as qe_configuration,
)
from projectkoios.frankensteins.io.quantumespresso.input import PwInput, PwInputWriter
from projectkoios.frankensteins.io.quantumespresso.inputfile.base import (
    QeAtomicPositionsCard,
    QeAtomicSpeciesCard,
    QeCellCard,
    QeCellParametersCard,
    QeControlCard,
    QeElectronsCard,
    QeIonsCard,
    QeKpointsCard,
    QeSystemCard,
)

from .declarations import (
    QeRelaxationAtomicPosition,
    QeRelaxationAtomicPositionsCard,
    QeRelaxationAtomicSpeciesCard,
    QeRelaxationCellNamelist,
    QeRelaxationCellParametersCard,
    QeRelaxationControlNamelist,
    QeRelaxationElectronsNamelist,
    QeRelaxationInputDeclaration,
    QeRelaxationIonsNamelist,
    QeRelaxationKPointsCard,
    QeRelaxationSystemNamelist,
)
from .enumerations import (
    QE_RELAXATION_ENUM_DESCRIPTIONS,
    QeNativeValueStatus,
    QeRelaxationCalculation,
    QeRelaxationCellDegreesOfFreedom,
    QeRelaxationCellDynamics,
    QeRelaxationIonDynamics,
)


@dataclass(frozen=True, slots=True)
class QeRelaxationInputRenderer:
    """Render one typed QE declaration through nominal namelist/card records."""

    coordinate_precision: int

    def __post_init__(self) -> None:
        if type(self.coordinate_precision) is not int or self.coordinate_precision <= 0:
            raise ValueError("coordinate_precision must be a positive integer")

    def render(self, declaration: QeRelaxationInputDeclaration) -> str:
        """Return deterministic QE input without applying scientific defaults."""
        if type(declaration) is not QeRelaxationInputDeclaration:
            raise TypeError("declaration must be a QeRelaxationInputDeclaration")
        control = declaration.control
        system = declaration.system
        groups = [
            QeControlCard(
                lines=(
                    f"calculation = '{control.calculation.value}'",
                    f"nstep = {control.maximum_ionic_steps}",
                    f"etot_conv_thr = {control.total_energy_tolerance_ry:.10e}",
                    f"forc_conv_thr = {control.force_tolerance_ry_per_bohr:.10e}",
                    f"tprnfor = {self._logical(control.print_forces)}",
                    f"tstress = {self._logical(control.calculate_stress)}",
                    f"prefix = '{control.prefix}'",
                    f"pseudo_dir = '{control.pseudo_dir}'",
                    f"outdir = '{control.outdir}'",
                )
            ).to_input_group(),
            QeSystemCard(
                lines=(
                    f"ibrav = {system.ibrav}",
                    f"nat = {system.atom_count}",
                    f"ntyp = {system.species_count}",
                    f"ecutwfc = {system.wavefunction_cutoff_ry:.10f}",
                    f"ecutrho = {system.charge_density_cutoff_ry:.10f}",
                )
            ).to_input_group(),
            QeElectronsCard(
                lines=(
                    f"conv_thr = {declaration.electrons.convergence_tolerance_ry:.10e}",
                )
            ).to_input_group(),
            QeIonsCard(
                lines=(f"ion_dynamics = '{declaration.ions.ion_dynamics.value}'",)
            ).to_input_group(),
        ]
        if declaration.cell is not None:
            cell = declaration.cell
            groups.append(
                QeCellCard(
                    lines=(
                        f"cell_dynamics = '{cell.cell_dynamics.value}'",
                        f"press = {cell.target_pressure_kbar:.10f}",
                        f"press_conv_thr = {cell.pressure_tolerance_kbar:.10f}",
                        f"cell_dofree = '{cell.degrees_of_freedom.value}'",
                    )
                ).to_input_group()
            )
        precision = self.coordinate_precision
        groups.extend(
            (
                QeAtomicSpeciesCard(
                    lines=tuple(
                        f"{item.symbol} {item.mass_amu:.10g} "
                        f"{item.pseudopotential_filename}"
                        for item in declaration.atomic_species.entries
                    )
                ).to_input_group(),
                QeCellParametersCard(
                    option=f"({declaration.cell_parameters.unit})",
                    lines=tuple(
                        self._vector(vector, precision)
                        for vector in declaration.cell_parameters.vectors
                    ),
                ).to_input_group(),
                QeAtomicPositionsCard(
                    option=f"({declaration.atomic_positions.unit})",
                    lines=tuple(
                        f"{item.symbol} "
                        f"{self._vector(item.fractional_position, precision)}"
                        for item in declaration.atomic_positions.positions
                    ),
                ).to_input_group(),
                QeKpointsCard(
                    option=declaration.k_points.option,
                    lines=(
                        " ".join(
                            str(value)
                            for value in (
                                *declaration.k_points.mesh,
                                *declaration.k_points.shift,
                            )
                        ),
                    ),
                ).to_input_group(),
            )
        )
        return PwInputWriter().render(PwInput(groups=tuple(groups)))

    @staticmethod
    def _logical(value: bool) -> str:
        return ".true." if value else ".false."

    @staticmethod
    def _vector(vector: tuple[float, float, float], precision: int) -> str:
        return " ".join(f"{value:.{precision}f}" for value in vector)


@dataclass(frozen=True, slots=True)
class QeRelaxationInputProjector:
    """Create and render card-based QE input from one generic request."""

    configuration: qe_configuration.QeRelaxationProjectionConfiguration

    def __post_init__(self) -> None:
        if (
            type(self.configuration)
            is not qe_configuration.QeRelaxationProjectionConfiguration
        ):
            raise TypeError(
                "configuration must be a QeRelaxationProjectionConfiguration"
            )

    def declare(self, request: PwDftRelaxationRequest) -> QeRelaxationInputDeclaration:
        """Return the complete typed native declaration before text rendering."""
        if type(request) is not PwDftRelaxationRequest:
            raise TypeError("request must be a PwDftRelaxationRequest")
        config = self.configuration
        calculation = {
            PwDftRelaxationScope.ATOMIC_POSITIONS: QeRelaxationCalculation.RELAX,
            PwDftRelaxationScope.ATOMIC_POSITIONS_AND_CELL: (
                QeRelaxationCalculation.VC_RELAX
            ),
        }[request.scope]
        self._validate_native_policy(calculation)
        atoms = request.simulation.unit_cell.atomic_basis.atoms
        if {atom.symbol for atom in atoms} != {item.symbol for item in config.species}:
            raise ValueError("QE species must exactly match the unit cell")
        cutoff_ry = self._conversion_factor("eV", "Ry") * (
            request.sampling.wavefunction_cutoff_ev
        )
        convergence = request.convergence
        cell = None
        if calculation is QeRelaxationCalculation.VC_RELAX:
            if (
                convergence.target_pressure_kbar is None
                or convergence.pressure_tolerance_kbar is None
                or config.cell_dynamics is None
                or config.cell_degrees_of_freedom is None
            ):
                raise ValueError("vc-relax requires complete CELL declarations")
            cell = QeRelaxationCellNamelist(
                cell_dynamics=config.cell_dynamics,
                target_pressure_kbar=convergence.target_pressure_kbar,
                pressure_tolerance_kbar=convergence.pressure_tolerance_kbar,
                degrees_of_freedom=config.cell_degrees_of_freedom,
            )
        unit_cell = request.simulation.unit_cell
        length_factor = MODEL_SYSTEM_UNIT_CONVERTER.conversion_factor(
            unit_cell.H.unit, PhysicalUnit("angstrom")
        )
        vectors = tuple(
            self._triplet(vector.magnitude, factor=length_factor)
            for vector in (unit_cell.h1, unit_cell.h2, unit_cell.h3)
        )
        return QeRelaxationInputDeclaration(
            control=QeRelaxationControlNamelist(
                calculation=calculation,
                maximum_ionic_steps=convergence.maximum_ionic_steps,
                total_energy_tolerance_ry=(
                    convergence.total_energy_tolerance_ev
                    * self._conversion_factor("eV", "Ry")
                ),
                force_tolerance_ry_per_bohr=(
                    convergence.force_tolerance_ev_per_angstrom
                    * self._conversion_factor("eV/angstrom", "Ry/bohr")
                ),
                print_forces=True,
                calculate_stress=(
                    request.scope is PwDftRelaxationScope.ATOMIC_POSITIONS_AND_CELL
                ),
                prefix=config.prefix,
                pseudo_dir=config.pseudo_dir,
                outdir=config.outdir,
            ),
            system=QeRelaxationSystemNamelist(
                ibrav=0,
                atom_count=len(atoms),
                species_count=len(config.species),
                wavefunction_cutoff_ry=cutoff_ry,
                charge_density_cutoff_ry=(
                    cutoff_ry * config.charge_density_cutoff_ratio
                ),
            ),
            electrons=QeRelaxationElectronsNamelist(
                convergence_tolerance_ry=config.electronic_tolerance_ry
            ),
            ions=QeRelaxationIonsNamelist(ion_dynamics=config.ion_dynamics),
            cell=cell,
            atomic_species=QeRelaxationAtomicSpeciesCard(entries=config.species),
            cell_parameters=QeRelaxationCellParametersCard(
                unit="angstrom",
                vectors=(vectors[0], vectors[1], vectors[2]),
            ),
            atomic_positions=QeRelaxationAtomicPositionsCard(
                unit="crystal",
                positions=tuple(
                    QeRelaxationAtomicPosition(
                        symbol=atom.symbol,
                        fractional_position=self._triplet(
                            atom.position_fractional.magnitude,
                            factor=1.0,
                        ),
                    )
                    for atom in atoms
                ),
            ),
            k_points=QeRelaxationKPointsCard(
                option="automatic",
                mesh=request.sampling.kpoint_mesh,
                shift=request.sampling.kpoint_shift,
            ),
        )

    def project(
        self, request: PwDftRelaxationRequest
    ) -> PwDftRelaxationInputProjection:
        """Render the typed declaration into one deterministic ``pw.in`` file."""
        declaration = self.declare(request)
        config = self.configuration
        return PwDftRelaxationInputProjection(
            integration_id=CalculatorIntegrationId("quantum-espresso"),
            rendered_inputs=(
                PwDftRelaxationRenderedInput(
                    filename=config.input_filename,
                    text=QeRelaxationInputRenderer(
                        coordinate_precision=config.coordinate_precision
                    ).render(declaration),
                ),
            ),
            required_external_inputs=tuple(
                item.pseudopotential_filename for item in config.species
            ),
            qualification=(
                "QE 7.5 card-based projection. Native optimizer and cell controls "
                "remain QE-specific and do not establish cross-code equivalence."
            ),
        )

    def _validate_native_policy(self, calculation: QeRelaxationCalculation) -> None:
        config = self.configuration
        self._require_supported(config.ion_dynamics, calculation)
        if calculation is QeRelaxationCalculation.RELAX:
            if config.cell_dynamics is not None or (
                config.cell_degrees_of_freedom is not None
            ):
                raise ValueError("relax must not declare QE CELL controls")
            return
        if config.cell_dynamics is None or config.cell_degrees_of_freedom is None:
            raise ValueError("vc-relax requires cell dynamics and degrees of freedom")
        self._require_supported(config.cell_dynamics, calculation)
        self._require_supported(config.cell_degrees_of_freedom, calculation)
        if config.cell_dynamics is QeRelaxationCellDynamics.NONE:
            raise ValueError("cell_dynamics='none' does not relax the requested cell")
        if config.cell_degrees_of_freedom is QeRelaxationCellDegreesOfFreedom.IBRAV:
            raise ValueError("cell_dofree='ibrav' is incompatible with ibrav=0")
        valid_pairs = {
            QeRelaxationCellDynamics.BFGS: QeRelaxationIonDynamics.BFGS,
            QeRelaxationCellDynamics.DAMPED_PARRINELLO_RAHMAN: (
                QeRelaxationIonDynamics.DAMP
            ),
            QeRelaxationCellDynamics.DAMPED_WENTZCOVITCH: (
                QeRelaxationIonDynamics.DAMP
            ),
        }
        expected_ion_dynamics = valid_pairs.get(config.cell_dynamics)
        if expected_ion_dynamics is None or (
            config.ion_dynamics is not expected_ion_dynamics
        ):
            raise ValueError("QE ion and cell dynamics declarations are incompatible")

    @staticmethod
    def _require_supported(
        value: (
            QeRelaxationIonDynamics
            | QeRelaxationCellDynamics
            | QeRelaxationCellDegreesOfFreedom
        ),
        calculation: QeRelaxationCalculation,
    ) -> None:
        matches = tuple(
            item for item in QE_RELAXATION_ENUM_DESCRIPTIONS if item.value is value
        )
        if len(matches) != 1:
            raise ValueError(f"QE native value lacks one description: {value.value}")
        description = matches[0]
        if calculation not in description.allowed_calculations:
            raise ValueError(
                f"{description.variable}={value.value!r} is invalid for "
                f"{calculation.value}"
            )
        if description.status is not QeNativeValueStatus.SUPPORTED:
            raise ValueError(f"{description.variable}={value.value!r} is not supported")

    @staticmethod
    def _conversion_factor(source: str, target: str) -> float:
        return MODEL_SYSTEM_UNIT_CONVERTER.conversion_factor(
            PhysicalUnit(source), PhysicalUnit(target)
        )

    @staticmethod
    def _triplet(
        values: NDArray[np.float64], *, factor: float
    ) -> tuple[float, float, float]:
        first, second, third = values
        return (
            float(first) * factor,
            float(second) * factor,
            float(third) * factor,
        )
