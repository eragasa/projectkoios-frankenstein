"""Project calculator-neutral SCF requests into Quantum ESPRESSO input."""

from __future__ import annotations

from dataclasses import dataclass

from physkit.units import MODEL_SYSTEM_UNIT_CONVERTER, PhysicalUnit, ScalarQuantity

from projectkoios.frankensteins.applications.pw_dft_scf.base import (
    CalculatorIntegrationId,
    PwDftScfRequest,
)
from projectkoios.frankensteins.applications.pw_dft_scf.integration import (
    PwDftScfInputProjection,
    PwDftScfRenderedInput,
)
from projectkoios.frankensteins.integrations.quantumespresso.input import (
    QePwInputFileAssembler,
)
from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_scf import (
    configuration as qe_configuration,
)
from projectkoios.frankensteins.io.quantumespresso.input import (
    PwInputGroup,
    PwInputWriter,
)

QE_SCF_INTEGRATION_ID = CalculatorIntegrationId(value="quantum-espresso")


@dataclass(frozen=True, slots=True)
class QeScfInputProjector:
    """Render one common SCF request using explicit QE-native policy."""

    configuration: qe_configuration.QeScfProjectionConfiguration

    def __post_init__(self) -> None:
        if (
            type(self.configuration)
            is not qe_configuration.QeScfProjectionConfiguration
        ):
            raise TypeError("configuration must be a QeScfProjectionConfiguration")

    def project(self, request: PwDftScfRequest) -> PwDftScfInputProjection:
        """Return deterministic ``pw.in`` text and pseudopotential requirements."""
        if type(request) is not PwDftScfRequest:
            raise TypeError("request must be a PwDftScfRequest")
        config = self.configuration
        atoms = request.simulation.unit_cell.atomic_basis.atoms
        atom_symbols = {atom.symbol for atom in atoms}
        configured_symbols = {item.symbol for item in config.species}
        if atom_symbols != configured_symbols:
            raise ValueError(
                "QE species configuration must exactly match the unit cell"
            )
        cutoff_ry = self._ev_to_ry(request.sampling.wavefunction_cutoff_ev)
        charge_density_cutoff_ry = cutoff_ry * config.charge_density_cutoff_ratio
        mesh = request.sampling.kpoint_mesh
        shift = request.sampling.kpoint_shift
        input_file = QePwInputFileAssembler().assemble(
            simulation=request.simulation,
            groups=(
                PwInputGroup(
                    kind="namelist",
                    tag="&SYSTEM",
                    lines=(
                        "ibrav = 0,",
                        f"nat = {len(atoms)},",
                        f"ntyp = {len(config.species)},",
                        f"ecutwfc = {cutoff_ry:.10f},",
                        f"ecutrho = {charge_density_cutoff_ry:.10f}",
                    ),
                ),
                PwInputGroup(
                    kind="namelist",
                    tag="&ELECTRONS",
                    lines=(f"conv_thr = {config.electronic_tolerance_ry:.10e}",),
                ),
                PwInputGroup(
                    kind="card",
                    tag="ATOMIC_SPECIES",
                    lines=tuple(
                        f"{item.symbol} {item.mass_amu:.10g} "
                        f"{item.pseudopotential_filename}"
                        for item in config.species
                    ),
                ),
                PwInputGroup(
                    kind="card",
                    tag="K_POINTS automatic",
                    lines=(
                        f"{mesh[0]} {mesh[1]} {mesh[2]} "
                        f"{shift[0]} {shift[1]} {shift[2]}",
                    ),
                ),
            ),
            prefix=config.prefix,
            pseudo_dir=config.pseudo_dir,
            outdir=config.outdir,
            cell_parameters_unit="angstrom",
            atomic_positions_unit="crystal",
            coordinate_precision=config.coordinate_precision,
            card_order=(
                "ATOMIC_SPECIES",
                "CELL_PARAMETERS",
                "ATOMIC_POSITIONS",
                "K_POINTS",
            ),
        )
        return PwDftScfInputProjection(
            integration_id=QE_SCF_INTEGRATION_ID,
            rendered_inputs=(
                PwDftScfRenderedInput(
                    filename=config.input_filename,
                    text=PwInputWriter().render(input_file),
                ),
            ),
            required_external_inputs=tuple(
                item.pseudopotential_filename for item in config.species
            ),
            qualification=(
                "QE ibrav=0 projection with explicit angstrom cell vectors, crystal "
                "positions, automatic k-point sampling, and calculator-native SCF "
                "policy."
            ),
        )

    @staticmethod
    def _ev_to_ry(value: float) -> float:
        converted = MODEL_SYSTEM_UNIT_CONVERTER.convert_scalar(
            ScalarQuantity(
                magnitude=value,
                unit=PhysicalUnit(expression="eV"),
            ),
            PhysicalUnit(expression="Ry"),
        )
        return converted.magnitude
