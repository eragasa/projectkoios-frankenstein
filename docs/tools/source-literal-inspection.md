# Python literal source inspection

`tools/sources/python_literal_assignment.py` preserves the safe reusable part of
the completed example-tree migration: reading constrained Python literals
without importing or executing the source module.

The maintained boundary consists of:

- `PythonStringMappingAssignmentRequest`, naming a source path and assignment;
- `PythonStringMappingAssignmentReader`, the externally selected actionizer;
- `PythonStringMappingAssignmentResult`, containing immutable ordered entries;
- `PythonStringMappingEntry`, one immutable string pair.

The reader parses syntax with `ast.parse` and accepts one top-level assignment
whose value is a dictionary literal with unique, non-empty string-literal keys
and values. It rejects expressions, dictionary unpacking, duplicate keys,
multiple assignments, and malformed source. Statements elsewhere in the module
are never executed.

This reader is an inspection primitive, not a provenance authority. Source TOML
declarations remain authoritative for selected example-tree identities. The
reader must not be used to restore the former reverse migration from maintained
adapter constants into source declarations.
