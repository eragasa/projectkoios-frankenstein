# Development

## Environment

Python 3.14 is the maintained target.

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install --editable '.[development]'
```

## External conformance checkouts

Ordinary unit tests require no upstream source. Full conformance tests use
explicit environment variables:

```bash
git clone https://github.com/eragasa/pyflamestk .upstreams/pyflamestk
git -C .upstreams/pyflamestk checkout 5b8368cc88d91bc56f9cc1c8a7fa8d9ea3d6b359
git clone https://github.com/eragasa/pypospack .upstreams/pypospack
git -C .upstreams/pypospack checkout be453fa7191e55a0426f66e8b5b5b0b103c8b29d
export PYFLAMESTK_CHECKOUT="$PWD/.upstreams/pyflamestk"
export PYPOSPACK_CHECKOUT="$PWD/.upstreams/pypospack"
```

`.upstreams/` is ignored. Package code never performs these Git operations.
The pymatmc2 declaration is currently reference-only, so CI does not check out
or inspect pymatmc2 until a bounded Frankenstein engine is extracted.

## Reproducible vendoring

A checked-in recipe maps authorized source paths to bounded destinations. Check
or synchronize the MgO Buckingham selection with:

```bash
python3.14 tools/vendor_source_selection.py \
  examples/pypospack/MgO/buck/VENDORING.toml \
  --checkout "$PYPOSPACK_CHECKOUT" --check

python3.14 tools/vendor_source_selection.py \
  examples/pypospack/MgO/buck/VENDORING.toml \
  --checkout "$PYPOSPACK_CHECKOUT" --sync
```

The tool verifies repository, commit, tree, selected identities, and destination
containment. It reads committed Git blobs rather than the checkout worktree and
regenerates the representation's file-level provenance. `--check` is read-only.
A recipe is not authorization to alter a source pin.

## Verification

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check src/projectkoios/frankensteins tests tools
MYPYPATH=src .venv/bin/python -m mypy --strict src/projectkoios/frankensteins
empty_tree="$(git hash-object -t tree /dev/null)"
git diff --check "$empty_tree" HEAD
.venv/bin/python -m build --wheel
```

## Opt-in validation tests

The default Pytest configuration excludes tests marked `validation`. These are
longer-running numerical or statistical checks and remain distinct from unit
and reconstruction-conformance tests. Run them explicitly with:

```bash
.venv/bin/python -m pytest -q -m validation
```

The probability validation suite uses a large deterministic sample to check
support, expected moments, and histogram occupancy. Passing it validates the
implemented sampling distribution for that fixture; it does not establish
scientific validation of a complete materials workflow.

## Distribution boundary

The wheel contains maintained `projectkoios.frankensteins` modules. It contains
no upstream checkout, source archive, download helper, calculator executable,
or singular `projectkoios.frankensteins.integration` namespace.

## Documentation

Every maintained module and top-level class has a mirrored nested `index.md`
under `docs/`. `tests/repository/documentation/test__documentation_layout.py`
enforces page existence, public-symbol coverage, and resolving internal links.

Every target architectural module separately provides `index.md` plus
`architecture/`, `implementation/`, `specifications/`, and `testing/` views.
Architecture views describe the problem without class or package design;
implementation views own Mermaid class and dependency diagrams.

CI performs the complete verification sequence and checks both upstream
repositories out at exact commits solely for conformance tests.
