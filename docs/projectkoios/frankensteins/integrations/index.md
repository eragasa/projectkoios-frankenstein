# `projectkoios.frankensteins.integrations`

**Source:** `src/projectkoios/frankensteins/integrations/`

Calculator-specific reconstruction boundaries live here. Integrations inspect
verified evidence and return protected observations or deterministic in-memory
artifacts. They do not run external programs.

## Implemented integrations

- [`lammps`](lammps/index.md): template inspection, command intents, verified
  PyPosPack provenance, and deterministic LAMMPS data rendering.
- [`vasp`](vasp/index.md): read-only POSCAR structure inspection.

The plural `integrations` namespace is canonical. No singular `integration`
compatibility namespace is provided.
