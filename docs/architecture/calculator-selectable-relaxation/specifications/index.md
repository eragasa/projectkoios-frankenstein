# Specifications

- A generic relaxation request **MUST** state fixed-cell or variable-cell scope explicitly.
- Its `CalculationType` **MUST** agree with that scope.
- Fixed-cell requests **MUST NOT** contain pressure controls.
- Variable-cell requests **MUST** contain target-pressure and pressure-tolerance values.
- Every native enum value **MUST** have one reviewed description with context, authority, companion fields, support status, and qualification.
- Backend descriptions **MUST NOT** be used for dynamic imports or string-based routing.
- A registry **MUST** accept only nominal, implemented input integrations with unique stable IDs.
- QE projection **MUST** use `ibrav=0`, `CELL_PARAMETERS (angstrom)`, and `ATOMIC_POSITIONS (crystal)`.
- QE `ion_dynamics`, `cell_dynamics`, and `cell_dofree` compatibility **MUST** fail closed.
- Native optimizer names **MUST NOT** be presented as cross-calculator algorithm equivalence.
- Test-only values **MUST NOT** be presented as an accepted silicon relaxation policy.
