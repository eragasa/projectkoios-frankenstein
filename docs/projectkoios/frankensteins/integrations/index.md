# `projectkoios.frankensteins.integrations`

**Source:** `src/projectkoios/frankensteins/integrations/`

Application-specific boundaries live here. Integrations inspect verified
evidence and return protected observations or deterministic in-memory artifacts.
The shared [`BaseExecutor`](base/index.md) defines how a future maintained
integration accepts a typed request and explicit workspace; it performs no
execution itself.

## Implemented integrations

- [`BaseExecutor`](base/index.md): common abstract request/workspace/result
  execution boundary. No concrete executor currently ships.
- [`lammps`](lammps/index.md): template inspection, command intents, verified
  PyPosPack provenance, and deterministic LAMMPS data rendering.
- [`quantumespresso`](quantumespresso/index.md): Quantum ESPRESSO-specific
  pseudopotential records inheriting calculator-neutral DFT contracts.
- [`vasp`](vasp/index.md): read-only POSCAR structure inspection.

The plural `integrations` namespace is canonical. No singular `integration`
compatibility namespace is provided.
