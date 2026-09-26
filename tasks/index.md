# Frankenstein task hierarchy

This repository-local hierarchy decomposes implementation work by technical owner and workflow owner. It is a temporary task record until `projectkoios-bootstrap` supplies an accepted task system.

Current disposition:

- [Active tasks](active.md)
- [Deferred tasks](deferred.md)
- [Closed tasks](closed.md)

Stable ownership hierarchy:

- [Calculator-neutral plane-wave DFT workflow tasks](workflow/dft/index.md)
- [Quantum ESPRESSO integration tasks](qe/index.md)
- [Quantum ESPRESSO workflow tasks](workflow/qe/index.md)
- [VASP integration tasks](vasp/index.md)
- [ABINIT integration tasks](abinit/index.md)
- [Wannier90 integration tasks](wannier/index.md)
- [Wannier90 workflow tasks](workflow/wannier/index.md)
- [Bulk composed workflows](workflow/bulk/index.md)
- [LAMMPS integration tasks](lammps/index.md)

A task's directory records ownership and decomposition, not priority. Reprioritization updates the disposition pages and the task's status statement without moving its directory.

Task records do not authorize calculator execution, commits, publication, or scientific acceptance. Git commits, tests, retained artifacts, and validation reports remain implementation evidence.
