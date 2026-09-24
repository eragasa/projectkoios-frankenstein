# Security and external-source boundary

This repository maintains execution-disabled reconstruction code while referring
to source hosted in separate repositories.

## Trust boundaries

A caller explicitly supplies a local checkout. Maintained package code never
discovers, clones, downloads, imports, or executes that checkout. Repository
URLs, exact commits, Git tree identities, selected paths, SHA-256 digests, byte
sizes, and license identities are maintained as reviewable metadata.

Upstream Python, shell commands, calculator inputs, and scheduler settings are
data only. Reconstruction must not invoke source `eval()`, calculators,
schedulers, shells, or arbitrary commands.

## Filesystem controls

[`projectkoios.frankensteins.evidence`](../projectkoios/frankensteins/evidence/index.md)
provides descriptor-based reads and directory inspection. Descendant paths are
normalized and opened relative to a pinned root descriptor. Symbolic links,
special files, oversized files, excessive file counts, and detectable concurrent
mutation are rejected. Cryptographic identity checks bind all selected bytes.

## CI boundary

CI checks external repositories out at exact commits into ignored workspace
paths. Tests receive those paths through explicit environment variables. Built
wheels contain maintained package code only and no external checkout content.

## Residual limits

The controls do not defend against a compromised kernel, filesystem, Python
runtime, Git host, or caller-selected root. Metadata comparison detects ordinary
concurrent writes but is not an atomic filesystem transaction. Exact file hashes
remain the content-identity boundary. Reconstruction establishes deterministic
software behavior and provenance only, not numerical verification, scientific
validation, or calculator safety.
