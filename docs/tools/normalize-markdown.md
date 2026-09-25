# Markdown normalization

`tools/normalize_markdown.py` removes AI-style hard wrapping from prose paragraphs so Markdown source remains readable in Obsidian. It preserves structural Markdown, including fenced code and Mermaid diagrams, headings, tables, front matter, math blocks, simple lists and block quotes, Obsidian callouts, and explicit hard breaks. Blank lines immediately before and after display-math blocks (`$$…$$`) are removed.

The script requires an explicit operation and one or more files or directories:

```bash
.venv/bin/python tools/normalize_markdown.py --check docs
.venv/bin/python tools/normalize_markdown.py --write docs/projectkoios/frankensteins/io/vasp/incar
```

Directories are scanned recursively for `.md` files. `--check` performs no writes and returns status 1 when normalization is needed. `--write` uses an atomic replacement in the file's directory while preserving its permission mode. Invalid paths, symbolic links, mixed line endings, invalid UTF-8, and files larger than 10 MB stop the operation with status 2. The operation does not follow links, access the network, inspect hidden configuration, or execute rendered content.

The normalizer is intentionally conservative. It does not reflow tables, nested list structures, HTML, fenced content, or explicit hard-break paragraphs. Review changes before committing. Its generic Markdown behavior may be reusable elsewhere, but the script and tests remain owned by this repository until a coordinator accepts a shared home.
