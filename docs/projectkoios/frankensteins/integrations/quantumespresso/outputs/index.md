# `projectkoios.frankensteins.integrations.quantumespresso.outputs`

Quantum ESPRESSO output support is composed from a `base` module and one module per native or captured output-file family. Generic result types preserve the concrete source-file type, and concrete file, parser, and result classes are closed with `@final`. The package does not re-export those implementations.
