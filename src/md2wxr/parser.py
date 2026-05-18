"""Parse Markdown files into title and HTML body."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import markdown


@dataclass
class ParsedPost:
    """Result of parsing a Markdown file."""

    title: str
    body_html: str


def parse_markdown_file(path: str | Path) -> ParsedPost:
    """Parse a Markdown file, extracting the first H1 as the title.

    The first ``# Heading`` line becomes the post title. Everything
    after it is converted to HTML for the post body. If no H1 is
    found, the filename (without extension) is used as the title
    and the entire file is converted to HTML.
    """
    text = Path(path).read_text(encoding="utf-8")
    return parse_markdown(text, fallback_title=Path(path).stem)


def parse_markdown(text: str, fallback_title: str = "Untitled") -> ParsedPost:
    """Parse a Markdown string into a title and HTML body."""
    title, body_md = _split_title(text, fallback_title)
    body_html = _convert_to_html(body_md)
    return ParsedPost(title=title, body_html=body_html)


def _split_title(text: str, fallback: str) -> tuple[str, str]:
    """Extract the first ATX H1 heading and return (title, remaining_md).

    Supports both ``# Title`` and underline-style headings using ``=``.
    """
    lines = text.split("\n")

    for i, line in enumerate(lines):
        # ATX-style: # Title
        m = re.match(r"^#\s+(.+?)(?:\s+#*\s*)?$", line)
        if m:
            title = m.group(1).strip()
            remaining = "\n".join(lines[i + 1 :]).lstrip("\n")
            return title, remaining

        # Setext-style: Title followed by ====
        if i + 1 < len(lines) and re.match(r"^=+\s*$", lines[i + 1]):
            title = line.strip()
            remaining = "\n".join(lines[i + 2 :]).lstrip("\n")
            return title, remaining

    return fallback, text


def _convert_to_html(md_text: str) -> str:
    """Convert Markdown to HTML using the markdown library."""
    md = markdown.Markdown(
        extensions=[
            "markdown.extensions.fenced_code",
            "markdown.extensions.tables",
            "markdown.extensions.codehilite",
            "markdown.extensions.toc",
        ],
        extension_configs={
            "markdown.extensions.codehilite": {
                "css_class": "highlight",
                "guess_lang": False,
            },
        },
    )
    return md.convert(md_text)
