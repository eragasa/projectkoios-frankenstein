"""Read-only VASP input-evidence boundary.

This namespace inspects VASP-format structures. It does not select POTCAR data,
construct calculator jobs, or execute VASP.
"""

from projectkoios.frankensteins.integrations.vasp.poscar import (
    VaspStructureObservation,
    inspect_poscar,
)

__all__ = ["VaspStructureObservation", "inspect_poscar"]
