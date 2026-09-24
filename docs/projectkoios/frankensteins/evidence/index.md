# `projectkoios.frankensteins.evidence`

**Source:** `src/projectkoios/frankensteins/evidence.py`

This module owns bounded filesystem reads for maintained reconstructions. It
pins a trusted evidence root with a directory descriptor, opens every descendant
relative to that descriptor, and refuses symbolic-link traversal.

## `read_bounded_regular_file`

`read_bounded_regular_file(root, relative_path, *, maximum_bytes, label)` reads
one normalized root-relative path. It:

- rejects absolute, parent-traversing, and non-normalized paths;
- opens directory components and the final file with no-follow flags;
- rejects non-regular files before consuming their contents;
- rejects declared or observed content beyond `maximum_bytes`;
- compares device, inode, mode, size, modification time, and change time before
  and after the read; and
- returns bytes only after the descriptor stayed stable for the complete read.

## `list_regular_files`

`list_regular_files(root, relative_directory, *, maximum_files, label)` returns
sorted POSIX-style paths relative to the selected directory. Traversal rejects
symbolic links, special files, count overflow, and directory metadata changes
during inspection.

Callers that need a stable tree inventory compare listings before and after
reading its files. Callers separately validate cryptographic hashes; safe reads
do not replace provenance verification.

## Limits

The passed `root` is the trust boundary. The module pins that directory but does
not authenticate the operating system, filesystem, or ancestors above it. The
no-follow descriptor operations require the POSIX behavior used by supported
macOS and Linux verification environments. These functions read evidence only;
they never import or execute it.
