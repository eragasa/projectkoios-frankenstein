# `SourceFileEvidence`

**Source:** `src/projectkoios/frankensteins/core.py`

Immutable identity for one explicitly selected upstream source file.

## Fields

- `relative_path`: normalized repository-relative POSIX path.
- `sha256`: exact lowercase SHA-256 digest.
- `byte_size`: nonnegative bounded size.

## Methods

- `to_dict()` returns deterministic JSON-ready identity material.

The model stores no local checkout path and grants no execution authority.
