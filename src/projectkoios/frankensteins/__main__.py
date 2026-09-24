from __future__ import annotations

import argparse
from pathlib import Path

from projectkoios.frankensteins.engines.pyflamestk_lmps_mgo_serial_uniform import (
    reconstruct_checkout,
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="koios-frankenstein")
    subcommands = result.add_subparsers(dest="command", required=True)
    inspect = subcommands.add_parser(
        "inspect-pyflamestk-mgo",
        help="build the execution-disabled MgO uniform-sampling recipe",
    )
    inspect.add_argument("--pyflamestk-checkout", type=Path, required=True)
    inspect.add_argument("--output", type=Path)
    return result


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    if args.command != "inspect-pyflamestk-mgo":
        raise AssertionError("unreachable command")
    recipe = reconstruct_checkout(args.pyflamestk_checkout.resolve())
    payload = recipe.to_json()
    if args.output is None:
        print(payload, end="")
        return 0
    output = args.output.absolute()
    if output.exists() or output.is_symlink():
        raise SystemExit(f"refusing to overwrite recipe output: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        stream.write(payload)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
