# `projectkoios.frankensteins.integrations.quantumespresso`

Quantum ESPRESSO-specific specializations of calculator-neutral simulation records. [`input`](input/index.md) projects shared plane-wave DFT settings into QE input models. [`outputs`](outputs/index.md) composes a base output contract with one module per native or captured output-file family. [`execution`](execution/index.md) resolves exact repository pseudopotentials, stages verified inputs, and executes `pw.x` with durable failure records. The package binds represented data to Quantum ESPRESSO formats without selecting scientific settings, accessing external files, or executing calculator processes.

[`pw_dft_relaxation`](pw_dft_relaxation/index.md) owns typed QE 7.5 relaxation namelist/card declarations and deterministic input projection.
