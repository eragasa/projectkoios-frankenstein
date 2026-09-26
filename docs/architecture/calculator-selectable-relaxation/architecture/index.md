# Architecture

A generic workflow needs to select QE, VASP, or ABINIT without pretending that their optimizers, convergence criteria, or input syntaxes are equivalent.

```mermaid
flowchart TD
    R[Calculator-neutral relaxation request]
    I[Stable integration ID value]
    W[Input wrapper and registry]
    Q[QE namelists and cards]
    V[VASP INCAR KPOINTS POSCAR]
    A[ABINIT datasets and variables]
    R --> W
    I --> W
    W --> Q
    W --> V
    W --> A
```

The request owns shared scientific quantities: geometry scope, sampling, energy and force thresholds, pressure controls, and bounded ionic steps. Each integration owns its native optimizer and cell controls.

Descriptions record purpose, authority, support, companion fields, and qualifications. They support review and validation but never perform dynamic dispatch. Registry lookup uses structurally comparable `CalculatorIntegrationId` values.
