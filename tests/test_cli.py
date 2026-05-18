"""Tests for md2wxr.cli."""

from pathlib import Path

from md2wxr.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


class TestCLI:
    def test_basic_conversion(self, tmp_path):
        output = tmp_path / "out.xml"
        main([str(FIXTURES / "sample.md"), "-o", str(output)])
        assert output.exists()
        content = output.read_text()
        assert "My Test Post" in content
        assert "wp:wxr_version" in content
        assert "<![CDATA[" in content

    def test_default_output_name(self, tmp_path, monkeypatch):
        src = tmp_path / "mypost.md"
        src.write_text("# Post Title\n\nHello.")
        monkeypatch.chdir(tmp_path)
        main([str(src)])
        expected = tmp_path / "mypost.xml"
        assert expected.exists()

    def test_custom_title(self, tmp_path):
        output = tmp_path / "out.xml"
        main(
            [
                str(FIXTURES / "sample.md"),
                "-o",
                str(output),
                "--title",
                "Override Title",
            ]
        )
        content = output.read_text()
        assert "Override Title" in content

    def test_custom_status(self, tmp_path):
        output = tmp_path / "out.xml"
        main(
            [
                str(FIXTURES / "sample.md"),
                "-o",
                str(output),
                "--status",
                "publish",
            ]
        )
        content = output.read_text()
        assert "<![CDATA[publish]]>" in content

    def test_custom_author(self, tmp_path):
        output = tmp_path / "out.xml"
        main(
            [
                str(FIXTURES / "sample.md"),
                "-o",
                str(output),
                "--author",
                "janedoe",
            ]
        )
        content = output.read_text()
        assert "janedoe" in content

    def test_custom_date(self, tmp_path):
        output = tmp_path / "out.xml"
        main(
            [
                str(FIXTURES / "sample.md"),
                "-o",
                str(output),
                "--date",
                "2025-12-25",
            ]
        )
        content = output.read_text()
        assert "2025-12-25 00:00:00" in content

    def test_missing_input_file(self, tmp_path):
        import pytest

        with pytest.raises(SystemExit):
            main([str(tmp_path / "nonexistent.md")])

    def test_output_is_valid_xml(self, tmp_path):
        from xml.etree import ElementTree as ET

        output = tmp_path / "out.xml"
        main([str(FIXTURES / "sample.md"), "-o", str(output)])
        ET.parse(str(output))

    def test_version(self, capsys):
        import pytest

        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "md2wxr" in captured.out
