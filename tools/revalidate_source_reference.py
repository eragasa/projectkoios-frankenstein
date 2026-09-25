#!/usr/bin/env python3
"""Revalidate a source declaration against an explicit local Git checkout."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__:
    from tools.sources.revalidation import (
        RevalidationError,
        SourceReferenceRevalidationReportModel,
        SourceReferenceRevalidationReportSerializer,
        SourceReferenceRevalidationRequest,
        SourceReferenceRevalidator,
    )
else:
    from sources.revalidation import (  # type: ignore[import-not-found,no-redef]
        RevalidationError,
        SourceReferenceRevalidationReportModel,
        SourceReferenceRevalidationReportSerializer,
        SourceReferenceRevalidationRequest,
        SourceReferenceRevalidator,
    )


def _repository_root(start: Path) -> Path:
    resolved = start.resolve()
    for candidate in (resolved, *resolved.parents):
        if (candidate / "pyproject.toml").is_file() and (
            candidate / "sources"
        ).is_dir():
            return candidate
    raise RevalidationError(f"could not locate repository root from {start}")


def _report_document(
    model: SourceReferenceRevalidationReportModel,
) -> dict[str, object]:
    return {
        "schema_version": model.schema_version,
        "component": model.component,
        "disposition": model.disposition.value,
        "pin_change_authorized": model.pin_change_authorized,
        "repository": {
            "declared": model.repository.declared,
            "observed": model.repository.observed,
            "matches": model.repository.matches,
        },
        "revision": {
            "requested": model.revision.requested,
            "declared": model.revision.declared,
            "observed": model.revision.observed,
            "matches": model.revision.matches,
        },
        "tree": {
            "declared": model.tree.declared,
            "observed": model.tree.observed,
            "matches": model.tree.matches,
        },
        "license": {
            "path": model.license.path,
            "declared_sha256": model.license.declared_sha256,
            "observed_sha256": model.license.observed_sha256,
            "matches": model.license.matches,
        },
        "selected_files": [
            {
                "path": item.path,
                "declared_sha256": item.declared_sha256,
                "declared_byte_size": item.declared_byte_size,
                "observed_sha256": item.observed_sha256,
                "observed_byte_size": item.observed_byte_size,
                "matches_declared_identity": item.matches_declared_identity,
            }
            for item in model.selected_files
        ],
        "example_trees": [
            {
                "path": item.path,
                "declared": item.declared,
                "observed": item.observed,
                "matches": item.matches,
            }
            for item in model.example_trees
        ],
        "matches_declaration": model.matches_declaration,
    }


def _parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description=(
            "Revalidate a declared external source against committed objects in an "
            "explicit local checkout."
        )
    )
    result.add_argument("component", help="source declaration name under sources/")
    result.add_argument(
        "--checkout",
        type=Path,
        required=True,
        help="explicit operator-managed Git checkout",
    )
    result.add_argument(
        "--revision",
        help="candidate commit or tag; defaults to the declared revision",
    )
    result.add_argument(
        "--report-candidate",
        action="store_true",
        help=(
            "return success for a structurally complete differing identity report; "
            "this does not accept or update the candidate"
        ),
    )
    result.add_argument(
        "--output",
        type=Path,
        help="write deterministic JSON to this path instead of stdout",
    )
    return result


def main(arguments: list[str] | None = None) -> int:
    options = _parser().parse_args(arguments)
    try:
        request = SourceReferenceRevalidationRequest(
            repository_root=_repository_root(Path(__file__)),
            component=options.component,
            checkout=options.checkout,
            requested_revision=options.revision,
        )
        result = SourceReferenceRevalidator().actionize(request)
    except RevalidationError as error:
        print(f"revalidation error: {error}", file=sys.stderr)
        return 2

    model = SourceReferenceRevalidationReportSerializer().serialize(result)
    encoded = json.dumps(_report_document(model), indent=2, sort_keys=True) + "\n"
    if options.output is None:
        sys.stdout.write(encoded)
    else:
        options.output.write_text(encoded, encoding="utf-8")

    if result.matches_declaration or options.report_candidate:
        return 0
    print(
        "source identity differs from the declaration; use --report-candidate only "
        "for an observational candidate report",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
