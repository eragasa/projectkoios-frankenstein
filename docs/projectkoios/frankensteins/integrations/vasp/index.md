# `projectkoios.frankensteins.integrations.vasp`

**Source:** `src/projectkoios/frankensteins/integrations/vasp/`

Read-only VASP input-evidence boundary. The package facade re-exports
`VaspStructureObservation` and `inspect_poscar` from [`poscar`](poscar/index.md).

The integration inspects structure text only. It does not select POTCAR data,
construct VASP jobs, write inputs, execute VASP, or claim scientific validity.
