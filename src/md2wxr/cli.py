"""Command-line interface for md2wxr."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from md2wxr import __version__
from md2wxr.parser import parse_markdown_file
from md2wxr.wxr import WXRPost, generate_wxr


def main(argv: list[str] | None = None) -> None:
    """Entry point for the md2wxr CLI."""
    args = _parse_args(argv)

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.with_suffix(".xml")

    parsed = parse_markdown_file(input_path)

    title = args.title if args.title else parsed.title
    post_date = _parse_date(args.date) if args.date else None

    post = WXRPost(
        title=title,
        content_html=parsed.body_html,
        author=args.author,
        status=args.status,
        post_date=post_date,
    )

    wxr_xml = generate_wxr(post)
    output_path.write_text(wxr_xml, encoding="utf-8")
    print(f"Wrote {output_path}")


def _parse_date(date_str: str) -> datetime:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        print(
            f"Error: invalid date format '{date_str}', expected YYYY-MM-DD",
            file=sys.stderr,
        )
        sys.exit(1)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="md2wxr",
        description="Convert Markdown files to WordPress WXR export XML.",
    )
    parser.add_argument(
        "input",
        help="path to the Markdown file to convert",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output XML file path (default: input file with .xml extension)",
    )
    parser.add_argument(
        "--title",
        help="override the post title (default: first H1 heading in the file)",
    )
    parser.add_argument(
        "--status",
        default="draft",
        choices=["draft", "publish", "private", "pending"],
        help="post status (default: draft)",
    )
    parser.add_argument(
        "--author",
        default="admin",
        help="author login name (default: admin)",
    )
    parser.add_argument(
        "--date",
        help="post date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    main()
