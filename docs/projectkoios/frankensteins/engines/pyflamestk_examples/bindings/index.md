# `pyflamestk_examples.bindings`

**Source:** `src/projectkoios/frankensteins/engines/pyflamestk_examples/bindings.py`

This module owns the exact example-root and Git-tree registry extracted from the
bound PyFlamestk source. `PyflamestkExampleEngineBinding` is the immutable
binding type. `SOURCE_EXAMPLE_TREES` preserves all seventeen
engine-shaped source paths. `ENGINE_BINDINGS` adds stable names, entrypoints,
reconstruction dispositions, duplicate-content relationships, and explicit
blockers. `engine_binding(engine_name)` performs exact lookup and rejects an
unknown name.

The registry contains sixteen reconstructable paths representing fourteen
unique source trees, two duplicate-content paths, and one blocked path. The
Tersoff path is reconstructable only as an execution-disabled declaration with
explicit historical-source warnings. A blocked binding is evidence about a
current parser limit, not an authorization to weaken the parser or execute the
historical workflow.
