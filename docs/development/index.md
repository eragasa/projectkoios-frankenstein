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

## Distribution boundary

The wheel contains maintained `projectkoios.frankensteins` modules. It contains
no upstream checkout, source archive, download helper, calculator executable,
or singular `projectkoios.frankensteins.integration` namespace.

## Documentation

Every maintained module and top-level class has a mirrored nested `index.md`
under `docs/`. `tests/test_documentation_layout.py` enforces page existence,
public-symbol coverage, and resolving internal links.

CI performs the complete verification sequence and checks both upstream
repositories out at exact commits solely for conformance tests.
