from __future__ import annotations

import unittest

from tools.normalize_markdown import normalize_markdown_text


class NormalizeMarkdownTextTest(unittest.TestCase):
    def test_unwraps_plain_prose(self) -> None:
        source = (
            "This paragraph was wrapped by an AI at approximately eighty\n"
            "characters even though the Markdown renderer should receive one line.\n"
        )

        self.assertEqual(
            normalize_markdown_text(source),
            "This paragraph was wrapped by an AI at approximately eighty characters "
            "even though the Markdown renderer should receive one line.\n",
        )

    def test_preserves_fenced_code_tables_and_hard_breaks(self) -> None:
        source = """# Heading

```mermaid
flowchart LR
    A --> B
```

| A | B |
|---|---|
| 1 | 2 |

first line  
second line
"""

        self.assertEqual(normalize_markdown_text(source), source)

    def test_removes_blank_lines_around_display_math(self) -> None:
        source = """Before.

$$
E = mc^2
$$

Between.

$$a^2 + b^2 = c^2$$

After.
"""

        self.assertEqual(
            normalize_markdown_text(source),
            "Before.\n$$\nE = mc^2\n$$\nBetween.\n$$a^2 + b^2 = c^2$$\nAfter.\n",
        )

    def test_unwraps_simple_list_items_and_block_quotes(self) -> None:
        source = """- A list item that was wrapped
  onto another source line.
- A second item.

> A quoted paragraph that was
> wrapped onto another line.
"""

        self.assertEqual(
            normalize_markdown_text(source),
            "- A list item that was wrapped onto another source line.\n"
            "- A second item.\n\n"
            "> A quoted paragraph that was wrapped onto another line.\n",
        )

    def test_preserves_front_matter_and_obsidian_callout(self) -> None:
        source = """---
title: Example
aliases:
  - Sample
---

> [!NOTE]
> Keep the callout structure
> on separate source lines.
"""

        self.assertEqual(normalize_markdown_text(source), source)


if __name__ == "__main__":
    unittest.main()
