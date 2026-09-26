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

The maintained [source revalidation tool](../tools/revalidate-source-reference.md)
requires an explicit checkout and verifies declared Git identities, selected-file
hashes and sizes, example trees, and license evidence. Runtime calculator
integrations separately bound retained artifact paths, reject unsafe path forms,
and enforce configured byte limits. Neither boundary discovers or downloads an
upstream repository.

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
