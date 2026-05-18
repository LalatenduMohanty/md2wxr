"""Tests for md2wxr.parser."""

from pathlib import Path

from md2wxr.parser import parse_markdown, parse_markdown_file

FIXTURES = Path(__file__).parent / "fixtures"


class TestSplitTitle:
    def test_atx_h1_extracted(self):
        result = parse_markdown("# Hello World\n\nBody text here.")
        assert result.title == "Hello World"

    def test_body_excludes_title(self):
        result = parse_markdown("# Title\n\nParagraph one.\n\nParagraph two.")
        assert "<h1" not in result.body_html
        assert "Paragraph one." in result.body_html
        assert "Paragraph two." in result.body_html

    def test_setext_h1_extracted(self):
        result = parse_markdown("My Title\n========\n\nBody here.")
        assert result.title == "My Title"
        assert "Body here." in result.body_html

    def test_fallback_title_when_no_h1(self):
        result = parse_markdown("## Only H2\n\nSome text.", fallback_title="fallback")
        assert result.title == "fallback"

    def test_h1_with_trailing_hashes(self):
        result = parse_markdown("# Title With Hashes ##\n\nBody.")
        assert result.title == "Title With Hashes"


class TestHtmlConversion:
    def test_bold_and_italic(self):
        result = parse_markdown("# T\n\n**bold** and *italic*")
        assert "<strong>bold</strong>" in result.body_html
        assert "<em>italic</em>" in result.body_html

    def test_links_preserved(self):
        result = parse_markdown("# T\n\n[click](https://example.com)")
        assert 'href="https://example.com"' in result.body_html

    def test_code_blocks(self):
        md = "# T\n\n```python\nprint('hi')\n```"
        result = parse_markdown(md)
        assert "print" in result.body_html

    def test_lists(self):
        md = "# T\n\n- one\n- two\n- three"
        result = parse_markdown(md)
        assert "<li>" in result.body_html
        assert "one" in result.body_html

    def test_h2_becomes_heading(self):
        md = "# T\n\n## Subtitle\n\nText."
        result = parse_markdown(md)
        assert "<h2" in result.body_html


class TestParseFile:
    def test_sample_fixture(self):
        result = parse_markdown_file(FIXTURES / "sample.md")
        assert result.title == "My Test Post"
        assert "<strong>bold</strong>" in result.body_html
        assert "<h2" in result.body_html
        assert "<li>" in result.body_html
