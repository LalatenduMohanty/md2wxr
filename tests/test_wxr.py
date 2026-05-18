"""Tests for md2wxr.wxr."""

from datetime import datetime, timezone
from xml.etree import ElementTree as ET

from md2wxr.wxr import WXRPost, generate_wxr

NAMESPACES = {
    "wp": "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
    "dc": "http://purl.org/dc/elements/1.1/",
}

FIXED_DATE = datetime(2026, 5, 17, tzinfo=timezone.utc)


def _make_post(**kwargs) -> WXRPost:
    defaults = {
        "title": "Test Post",
        "content_html": "<p>Hello world</p>",
        "post_date": FIXED_DATE,
    }
    defaults.update(kwargs)
    return WXRPost(**defaults)


def _parse_wxr(post: WXRPost) -> ET.Element:
    """Generate WXR and parse as XML, returning the root element."""
    xml_str = generate_wxr(post)
    return ET.fromstring(xml_str)


class TestWXRStructure:
    def test_xml_declaration(self):
        xml = generate_wxr(_make_post())
        assert xml.startswith('<?xml version="1.0" encoding="UTF-8" ?>')

    def test_wxr_version(self):
        root = _parse_wxr(_make_post())
        version = root.find(".//wp:wxr_version", NAMESPACES)
        assert version is not None
        assert version.text == "1.2"

    def test_wordpress_comment_block(self):
        xml = generate_wxr(_make_post())
        assert "This is a WordPress eXtended RSS file" in xml

    def test_generator_comment(self):
        xml = generate_wxr(_make_post())
        assert 'generator="md2wxr/0.1.0"' in xml

    def test_rss_namespaces(self):
        xml = generate_wxr(_make_post())
        assert "http://wordpress.org/export/1.2/" in xml
        assert "http://purl.org/rss/1.0/modules/content/" in xml
        assert "http://wordpress.org/export/1.2/excerpt/" in xml

    def test_base_urls(self):
        root = _parse_wxr(_make_post(site_url="https://myblog.com"))
        base_site = root.find(".//wp:base_site_url", NAMESPACES)
        base_blog = root.find(".//wp:base_blog_url", NAMESPACES)
        assert base_site is not None
        assert base_site.text == "https://myblog.com"
        assert base_blog is not None
        assert base_blog.text == "https://myblog.com"


class TestWXRAuthor:
    def test_default_author(self):
        xml = generate_wxr(_make_post())
        assert "admin" in xml

    def test_custom_author(self):
        xml = generate_wxr(_make_post(author="jdoe"))
        assert "jdoe" in xml


class TestWXRPost:
    def test_title_in_item(self):
        xml = generate_wxr(_make_post(title="My Great Post"))
        assert "My Great Post" in xml

    def test_content_in_cdata(self):
        xml = generate_wxr(_make_post(content_html="<p>Content here</p>"))
        assert "<![CDATA[<p>Content here</p>]]>" in xml

    def test_status_draft(self):
        xml = generate_wxr(_make_post(status="draft"))
        assert "<![CDATA[draft]]>" in xml

    def test_status_publish(self):
        xml = generate_wxr(_make_post(status="publish"))
        assert "<![CDATA[publish]]>" in xml

    def test_post_date_formatted(self):
        xml = generate_wxr(_make_post())
        assert "2026-05-17 00:00:00" in xml

    def test_post_type_is_post(self):
        xml = generate_wxr(_make_post())
        assert "<![CDATA[post]]>" in xml


class TestSlugify:
    def test_auto_slug(self):
        post = _make_post(title="Hello World: A Test!")
        assert post.slug == "hello-world-a-test"

    def test_explicit_slug(self):
        post = WXRPost(
            title="Test",
            content_html="<p>x</p>",
            slug="custom-slug",
            post_date=FIXED_DATE,
        )
        assert post.slug == "custom-slug"


class TestExcerpt:
    def test_auto_excerpt(self):
        post = _make_post(content_html="<p>This is a paragraph.</p>")
        assert "This is a paragraph." in post.excerpt

    def test_excerpt_strips_html(self):
        post = _make_post(
            content_html="<p><strong>Bold</strong> text</p>"
        )
        assert "<strong>" not in post.excerpt
        assert "Bold text" in post.excerpt

    def test_explicit_excerpt(self):
        post = WXRPost(
            title="T",
            content_html="<p>x</p>",
            excerpt="Custom excerpt",
            post_date=FIXED_DATE,
        )
        assert post.excerpt == "Custom excerpt"
