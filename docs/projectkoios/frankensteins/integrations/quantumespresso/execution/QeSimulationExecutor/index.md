# `QeSimulationExecutor`

The public `execute` action accepts a `QuantumEspressoSimulation`, explicit `PseudopotentialRepository`, `executable`, `working_directory`, and optional `timeout_seconds`. It requires `ControlBlock.pseudo_dir` to select the run directory, resolves and cryptographically verifies every declared pseudopotential, atomically stages inputs, and invokes `CalculatorExecutor`. Repository resolution or staging failures are recorded before an exception is raised.
