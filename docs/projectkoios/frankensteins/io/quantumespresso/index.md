# `projectkoios.frankensteins.io.quantumespresso`

Maintained Quantum ESPRESSO text-I/O boundary. It follows the useful separation in the historical PyPosPack VASP I/O surface while replacing mutable file handlers with immutable records and separate parsers or writers.

The package represents `pw.x` input and exact pseudopotential identities. Native output-file compositions belong to `projectkoios.frankensteins.integrations.quantumespresso.outputs`. This package does not select scientific settings, access files, execute Quantum ESPRESSO, normalize results into application QOIs, or claim numerical convergence or scientific validity.
