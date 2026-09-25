# `PoscarWriter`

`PoscarWriter.render` produces deterministic VASP 5 POSCAR text from a `PoscarModel`. `PoscarWriter.write` atomically writes that text to an explicit `Path`, rejects destination symlinks, and preserves an existing destination's permission mode.
