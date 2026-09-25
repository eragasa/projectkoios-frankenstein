# `PyflamestkExampleEngineBinding`

`PyflamestkExampleEngineBinding` inherits `BaseEngine` and adds the immutable
reconstruction disposition for one engine-shaped historical example. Its public
fields are:

- `engine_name`
- `example_root`
- `example_tree`
- `entrypoints`
- `status`
- `limitations`
- `content_alias_of`

Construction validates normalized source paths, exact Git tree identities,
root-level Python entrypoint names, supported dispositions, blocker evidence,
and content-alias names. A reconstructable binding cannot carry blockers; a
blocked binding must state at least one limitation.
