# `projectkoios.frankensteins.io.quantumespresso`

Maintained Quantum ESPRESSO text-I/O boundary. It follows the useful separation in the historical PyPosPack VASP I/O surface while replacing mutable file handlers with immutable records and separate parsers or writers.

The package represents `pw.x` input, selected raw output observations, and exact pseudopotential identities. It does not select scientific settings, access files, execute Quantum ESPRESSO, normalize results into application QOIs, or claim numerical convergence or scientific validity.
