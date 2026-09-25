# Project Koios Frankenstein

This repository owns provenance-bound, execution-disabled reconstructions of
externally hosted scientific workflows. It does not vendor, import, execute,
discover, clone, or download upstream source repositories at package runtime.

## Adapter and incubation architecture

- `Adapter` is the nominal containing role for maintained boundaries.
- A `Binding` adapts an imported or deliberately vendored code dependency.
- An `Integration` adapts an external application or service.
- Use base classes for shared nominal "is-a" relationships and composition for
  independent "has-a" relationships. An integration may contain a binding; it
  must not inherit from that binding.
- Do not invent a generic `adapt()` method from adapter membership alone.
- If another shared base class appears necessary, freeze that implementation
  work and hold an explicit architecture discussion before adding it.
- Treat `projectkoios.frankensteins` as a mirrored pick-and-pull incubation
  overlay. Target migration removes only the `frankensteins` namespace segment;
  it must not require class renaming or inheritance redesign.
- Keep shared namespace package levels free of broad implementation re-exports.
  Only provider leaves, deliberate facades, or composition roots may expose a
  curated API.
- Name repositories for capabilities, such as `projectkoios-lammps` or
  `projectkoios-github`; express binding and integration roles in Python
  namespaces instead of repository names.

## Source boundaries

- Use only operator-provided local checkouts for source inspection and
  conformance validation.
- Read committed Git objects; do not execute upstream Python, shell scripts,
  calculators, schedulers, or simulation engines.
- Exact commits, trees, selected-file hashes and sizes, and license hashes are
  provenance. Branch names and local checkout paths are not.
- Keep candidate reports outside the tracked repository. Reports are
  observational evidence, not durable runtime state and not authorization for a
  pin change.
- Preserve the distinction between reconstruction conformance, numerical
  verification, and scientific validation.

## Source revalidation

Use `tools/revalidate_source_reference.py` before inspecting or changing an
external source pin. The strict form verifies the current declaration:

```bash
python3.14 tools/revalidate_source_reference.py pyflamestk \
  --checkout "$PYFLAMESTK_CHECKOUT"
python3.14 tools/revalidate_source_reference.py pypospack \
  --checkout "$PYPOSPACK_CHECKOUT"
```

For a prospective commit or tag, produce a bounded candidate report:

```bash
python3.14 tools/revalidate_source_reference.py pyflamestk \
  --checkout "$HOME/repos/pyflamestk" \
  --revision v0.1.0 \
  --report-candidate \
  --output /tmp/pyflamestk-v0.1.0-revalidation.json
```

`--report-candidate` only permits the script to return success after producing a
structurally complete report. It does not accept the candidate, update files, or
establish behavioral conformance. Never commit the generated report.

A pin update must still deliberately update and validate all applicable items:

1. `sources/<component>.toml` repository, release tag, commit, tree, selected
   identities, and license identity;
2. implementation-bound provenance constants and source spans;
3. reconstruction and adversarial tests;
4. CI checkout revisions;
5. README and source documentation;
6. full conformance tests against the exact candidate commit; and
7. a final strict revalidation with no `--report-candidate` flag.

Stop rather than weakening an identity check when a selected file, license,
source span, repository origin, or Git object cannot be verified.

## Development verification

Run the maintained verification sequence after changes:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check src/projectkoios/frankensteins tests tools
MYPYPATH=src .venv/bin/python -m mypy --strict src/projectkoios/frankensteins
empty_tree="$(git hash-object -t tree /dev/null)"
git diff --check "$empty_tree" HEAD
.venv/bin/python -m build --wheel
```

The wheel must contain maintained reconstruction code only. It must not contain
upstream checkouts, source archives, revalidation reports, download helpers,
calculator executables, or duplicated legacy integration namespaces.
