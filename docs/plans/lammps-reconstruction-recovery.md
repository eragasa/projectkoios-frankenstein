# LAMMPS reconstruction recovery

## Status

This branch is an intentionally nonconformant recovery work surface. It preserves the last repository-owned LAMMPS reconstruction so that support can be repaired deliberately rather than abandoned or silently treated as maintained.

The recovered code must not be merged into a maintained branch until its imports, ownership boundaries, tests, documentation, provenance checks, and full verification are repaired. The recovery baseline has five expected test-collection errors because the historical code and tests still import the removed `projectkoios.frankensteins.core` and `projectkoios.frankensteins.evidence` modules.

## Recovery provenance

- Branch baseline: `aa0f2bd8ad23d4d2c2f24c236385f05b1d602f9e`.
- Recovered implementation source: `cd278d84dbb37d8454668bc3102951fe7a068546`, paths under `src/projectkoios/frankensteins/integrations/lammps/`.
- Recovered tests and mirrored documentation: `2564a3e08b8dea24c54459037f260769603e1aa3`, paths under `tests/projectkoios/frankensteins/integrations/lammps/` and `docs/projectkoios/frankensteins/integrations/lammps/`.
- Bound PyPosPack source declaration: `sources/pypospack.toml`.

These identities describe Project Koios recovery provenance. They do not alter or supersede the exact upstream identities in the source declaration.

## Known repair requirements

1. Replace dependencies on the removed `projectkoios.frankensteins.core` and `projectkoios.frankensteins.evidence` modules with narrow, maintained leaf-module contracts.
2. Remove broad package-level re-exports and update callers to explicit leaf-module imports.
3. Convert materially repaired internal records to frozen, slotted dataclasses.
4. Keep native LAMMPS input/output models inside the LAMMPS integration while keeping calculator-neutral simulation and workflow state outside it.
5. Separate data inspection, input rendering, execution requests, execution evidence, output parsing, and scientific normalization.
6. Preserve exact PyPosPack source identities and applicable license and attribution notices.
7. Do not import or execute historical upstream Python. Any future calculator execution requires an explicit maintained executor, operator-supplied resources, and opt-in authorization.
8. Mirror every maintained module and public type in tests and documentation, then pass the repository verification sequence before merge.

## Safety qualification

The recovered implementation and tests are historical scaffolding, not accepted runtime functionality. Reconstruction conformance, calculator execution, numerical verification, and scientific validation remain distinct claims.
