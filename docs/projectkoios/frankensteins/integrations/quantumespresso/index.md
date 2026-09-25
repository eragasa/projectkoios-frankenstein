# `projectkoios.frankensteins.integrations.quantumespresso`

Quantum ESPRESSO-specific specializations of calculator-neutral simulation records. [`input`](input/index.md) projects shared plane-wave DFT settings into QE input models. [`execution`](execution/index.md) resolves exact repository pseudopotentials, stages verified inputs, and executes `pw.x` with durable failure records. The package binds represented data to Quantum ESPRESSO formats without selecting scientific settings, accessing external files, or executing calculator processes.
