#!/usr/bin/env python3
"""Check or synchronize a provenance-authorized source selection."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__:
    from tools.vendors.source_selection import (
        VendoringDisposition,
        VendoringError,
        VendoringMode,
        VendorSourceSelectionActionizer,
        VendorSourceSelectionRequest,
    )
else:
    from vendors.source_selection import (  # type: ignore[import-not-found,no-redef]
        VendoringDisposition,
        VendoringError,
        VendoringMode,
        VendorSourceSelectionActionizer,
        VendorSourceSelectionRequest,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recipe", type=Path)
    parser.add_argument("--checkout", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--sync", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    repository_root = Path(__file__).resolve().parents[1]
    recipe_path = arguments.recipe
    if not recipe_path.is_absolute():
        recipe_path = repository_root / recipe_path
    request = VendorSourceSelectionRequest(
        repository_root=repository_root,
        recipe_path=recipe_path,
        checkout=arguments.checkout.resolve(),
        mode=VendoringMode.SYNC if arguments.sync else VendoringMode.CHECK,
    )
    try:
        result = VendorSourceSelectionActionizer().actionize(request)
    except VendoringError as error:
        print(f"vendoring error: {error}", file=sys.stderr)
        return 1
    message = (
        "vendored selection synchronized"
        if result.disposition is VendoringDisposition.SELECTION_SYNCHRONIZED
        else "vendored selection matches"
    )
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
