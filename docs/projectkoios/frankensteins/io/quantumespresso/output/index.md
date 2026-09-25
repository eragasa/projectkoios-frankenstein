# `projectkoios.frankensteins.io.quantumespresso.output`

`PwOutputParser` performs bounded extraction from `pw.x` standard output through `parse`. It returns an immutable `PwOutput` retaining native Rydberg and kilobar units, the last represented repeated scalar, completion and SCF markers, counts, and program version. `QuantumEspressoOutputError` identifies text with no supported evidence.

This parser is a compact OUTCAR-like observation surface. QEXSD remains the stronger source for production electronic-structure arrays and application normalization.
