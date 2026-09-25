#!/usr/bin/env python3
"""Normalize hard-wrapped Markdown prose without rewriting structural blocks."""

from __future__ import annotations

import argparse
import os
import re
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

if __package__:
    from tools.base import DataObjectActionizer, DataObjectRequest, DataObjectResult
else:
    from base import (  # type: ignore[import-not-found,no-redef]
        DataObjectActionizer,
        DataObjectRequest,
        DataObjectResult,
    )

_MAX_MARKDOWN_BYTES = 10_000_000
_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_LIST_ITEM = re.compile(r"^(\s{0,3}(?:[-+*]|\d+[.)])\s+)(.*)$")
_BLOCK_QUOTE = re.compile(r"^(\s*(?:>\s*)+)(.*)$")
_HEADING = re.compile(r"^\s{0,3}#{1,6}(?:\s+|$)")
_SETEXT = re.compile(r"^\s{0,3}(?:=+|-+)\s*$")
_THEMATIC = re.compile(r"^\s{0,3}(?:(?:\*\s*){3,}|(?:-\s*){3,}|(?:_\s*){3,})$")
_DEFINITION = re.compile(r"^\s{0,3}\[[^]]+\]:")
_HTML = re.compile(r"^\s{0,3}(?:<!--|</?[A-Za-z][^>]*>)")


@dataclass(frozen=True, slots=True)
class MarkdownNormalizationRequest(DataObjectRequest):
    """Select Markdown paths and an explicit check or write operation."""

    paths: tuple[Path, ...]
    operation: Literal["check", "write"]

    def __post_init__(self) -> None:
        if type(self.paths) is not tuple or not self.paths:
            raise ValueError("paths must be a nonempty tuple")
        if any(not isinstance(path, Path) for path in self.paths):
            raise TypeError("paths must contain Path values")
        if self.operation not in {"check", "write"}:
            raise ValueError("operation must be 'check' or 'write'")


@dataclass(frozen=True, slots=True)
class MarkdownNormalizationRecord:
    """Record whether one Markdown file differs from normalized text."""

    path: Path
    changed: bool


@dataclass(frozen=True, slots=True)
class MarkdownNormalizationResult(DataObjectResult):
    """Report every inspected file and the number requiring normalization."""

    records: tuple[MarkdownNormalizationRecord, ...]
    changed_count: int


class MarkdownNormalizer(
    DataObjectActionizer[MarkdownNormalizationRequest, MarkdownNormalizationResult]
):
    """Normalize explicit Markdown files with bounded, atomic filesystem effects."""

    def actionize(
        self, request: MarkdownNormalizationRequest, /
    ) -> MarkdownNormalizationResult:
        """Check or atomically rewrite the selected Markdown files."""
        if type(request) is not MarkdownNormalizationRequest:
            raise TypeError("request must be a MarkdownNormalizationRequest")
        files = _resolve_markdown_files(request.paths)
        records: list[MarkdownNormalizationRecord] = []
        for path in files:
            payload = path.read_bytes()
            if len(payload) > _MAX_MARKDOWN_BYTES:
                raise ValueError(f"Markdown file exceeds byte limit: {path}")
            text = payload.decode("utf-8")
            normalized = normalize_markdown_text(text)
            changed = normalized != text
            if changed and request.operation == "write":
                _atomic_write(path, normalized.encode("utf-8"))
            records.append(MarkdownNormalizationRecord(path=path, changed=changed))
        return MarkdownNormalizationResult(
            records=tuple(records),
            changed_count=sum(record.changed for record in records),
        )


def normalize_markdown_text(text: str) -> str:
    """Unwrap prose paragraphs while preserving Markdown structural constructs."""
    if type(text) is not str:
        raise TypeError("Markdown text must be a string")
    if "\r\n" in text:
        without_crlf = text.replace("\r\n", "")
        if "\r" in without_crlf or "\n" in without_crlf:
            raise ValueError("Markdown text has mixed line endings")
        newline = "\r\n"
        logical = text.replace("\r\n", "\n")
    else:
        if "\r" in text:
            raise ValueError("Markdown text has unsupported carriage returns")
        newline = "\n"
        logical = text

    final_newline = logical.endswith("\n")
    lines = logical.splitlines()
    output: list[str] = []
    index = 0

    if lines and lines[0] == "---":
        closing = next(
            (
                position
                for position in range(1, len(lines))
                if lines[position] in {"---", "..."}
            ),
            None,
        )
        if closing is not None:
            output.extend(lines[: closing + 1])
            index = closing + 1

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            output.append(line)
            index += 1
            continue
        if fence := _FENCE.match(line):
            index = _copy_fenced_block(lines, index, output, fence.group(1))
            continue
        if _is_math_block_start(line):
            index = _copy_math_block(lines, index, output)
            continue
        if list_item := _LIST_ITEM.match(line):
            index = _normalize_list_item(lines, index, output, list_item)
            continue
        if block_quote := _BLOCK_QUOTE.match(line):
            index = _normalize_block_quote(lines, index, output, block_quote.group(1))
            continue
        if _is_structural(line):
            output.append(line)
            index += 1
            continue

        paragraph: list[str] = []
        while index < len(lines):
            candidate = lines[index]
            if (
                not candidate.strip()
                or _FENCE.match(candidate)
                or _is_math_block_start(candidate)
                or _LIST_ITEM.match(candidate)
                or _BLOCK_QUOTE.match(candidate)
                or _is_structural(candidate)
            ):
                break
            paragraph.append(candidate)
            index += 1
        output.extend(_normalize_prose_lines(paragraph))

    normalized = "\n".join(output)
    if final_newline:
        normalized += "\n"
    return normalized.replace("\n", newline)


def _normalize_prose_lines(lines: list[str]) -> list[str]:
    if not lines:
        return []
    if any(_has_hard_break(line) for line in lines):
        return lines
    return [" ".join(line.strip() for line in lines)]


def _normalize_list_item(
    lines: list[str],
    index: int,
    output: list[str],
    match: re.Match[str],
) -> int:
    prefix, first_content = match.groups()
    base_indent = len(prefix) - len(prefix.lstrip())
    content = [first_content]
    cursor = index + 1
    while cursor < len(lines):
        candidate = lines[cursor]
        if not candidate.strip() or _LIST_ITEM.match(candidate):
            break
        leading = len(candidate) - len(candidate.lstrip(" "))
        if (
            leading <= base_indent
            or _FENCE.match(candidate)
            or _BLOCK_QUOTE.match(candidate)
            or _is_structural(candidate)
        ):
            break
        content.append(candidate.strip())
        cursor += 1
    if any(_has_hard_break(line) for line in content):
        output.append(lines[index])
        output.extend(lines[index + 1 : cursor])
    else:
        output.append(prefix + " ".join(part.strip() for part in content))
    return cursor


def _normalize_block_quote(
    lines: list[str], index: int, output: list[str], prefix: str
) -> int:
    contents: list[str] = []
    cursor = index
    while cursor < len(lines):
        match = _BLOCK_QUOTE.match(lines[cursor])
        if match is None or match.group(1) != prefix:
            break
        contents.append(match.group(2))
        cursor += 1
    if (
        not contents
        or contents[0].startswith("[!")
        or any(_has_hard_break(line) or _is_structural(line) for line in contents)
    ):
        output.extend(lines[index:cursor])
    else:
        output.append(prefix + " ".join(content.strip() for content in contents))
    return cursor


def _copy_fenced_block(
    lines: list[str], index: int, output: list[str], marker: str
) -> int:
    marker_character = marker[0]
    minimum_length = len(marker)
    output.append(lines[index])
    cursor = index + 1
    closing = re.compile(
        rf"^\s{{0,3}}{re.escape(marker_character)}{{{minimum_length},}}\s*$"
    )
    while cursor < len(lines):
        output.append(lines[cursor])
        if closing.match(lines[cursor]):
            return cursor + 1
        cursor += 1
    return cursor


def _copy_math_block(lines: list[str], index: int, output: list[str]) -> int:
    while output and not output[-1].strip():
        output.pop()
    opening = lines[index].strip()
    output.append(lines[index])
    cursor = index + 1
    if len(opening) > 4 and opening.endswith("$$"):
        return _skip_blank_lines(lines, cursor)
    while cursor < len(lines):
        output.append(lines[cursor])
        if lines[cursor].strip() == "$$":
            return _skip_blank_lines(lines, cursor + 1)
        cursor += 1
    return cursor


def _skip_blank_lines(lines: list[str], index: int) -> int:
    while index < len(lines) and not lines[index].strip():
        index += 1
    return index


def _is_math_block_start(line: str) -> bool:
    return line.strip().startswith("$$")


def _is_structural(line: str) -> bool:
    stripped = line.strip()
    return bool(
        _HEADING.match(line)
        or _SETEXT.match(line)
        or _THEMATIC.match(line)
        or _DEFINITION.match(line)
        or _HTML.match(line)
        or line.startswith("    ")
        or "|" in line
        or stripped.startswith(":::")
    )


def _has_hard_break(line: str) -> bool:
    return line.endswith("  ") or line.endswith("\\")


def _resolve_markdown_files(paths: tuple[Path, ...]) -> tuple[Path, ...]:
    files: dict[Path, None] = {}
    for supplied in paths:
        if supplied.is_symlink():
            raise ValueError(f"symbolic links are not accepted: {supplied}")
        if supplied.is_dir():
            candidates = sorted(supplied.rglob("*.md"))
        elif supplied.is_file() and supplied.suffix.casefold() == ".md":
            candidates = [supplied]
        else:
            raise ValueError(f"path is not a Markdown file or directory: {supplied}")
        for candidate in candidates:
            if candidate.is_symlink() or not candidate.is_file():
                raise ValueError(
                    f"non-regular Markdown path is not accepted: {candidate}"
                )
            files[candidate.resolve()] = None
    return tuple(sorted(files))


def _atomic_write(path: Path, payload: bytes) -> None:
    mode = stat.S_IMODE(path.stat().st_mode)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as temporary:
            temporary_name = temporary.name
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.chmod(temporary_name, mode)
        os.replace(temporary_name, path)
    finally:
        if temporary_name is not None and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unwrap Markdown prose while preserving structural blocks."
    )
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--check", action="store_true")
    operation.add_argument("--write", action="store_true")
    parser.add_argument("paths", nargs="+", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the explicit check or write operation and return a process status."""
    arguments = _parser().parse_args(argv)
    operation: Literal["check", "write"] = "write" if arguments.write else "check"
    try:
        result = MarkdownNormalizer().actionize(
            MarkdownNormalizationRequest(
                paths=tuple(arguments.paths),
                operation=operation,
            )
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(f"markdown normalization error: {error}", file=sys.stderr)
        return 2
    for record in result.records:
        if record.changed:
            disposition = (
                "normalized" if operation == "write" else "needs normalization"
            )
            print(f"{disposition}: {record.path}")
    if operation == "check" and result.changed_count:
        return 1
    file_count = len(result.records)
    print(f"markdown files checked: {file_count}; changed: {result.changed_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
