# Vendored PyPosPack VASP code

This directory preserves the complete VASP-related Python source selection from the
PyPosPack revision pinned by `sources/pypospack.toml`.

The files are copied byte-for-byte from committed Git objects. `PROVENANCE.json`
records the original path, Git blob identity, SHA-256 digest, byte size, and local
modification status for every file. `VENDORING.toml` is the reproducible extraction
recipe.

No vendored file is locally modified. The code is retained as historical implementation
evidence and is not an authorization to execute VASP. Imports outside the selected
VASP files continue to be supplied by the exactly pinned PyPosPack dependency.
