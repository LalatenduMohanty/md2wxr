# md2wxr

Convert Markdown files to WordPress WXR (WordPress eXtended RSS) export files.

The output XML is accepted by both **WordPress.com** and **self-hosted WordPress** via Tools > Import > WordPress.

## Why Markdown?

Markdown is a natural format for drafting blog posts. You can write offline in any text editor, iterate quickly, and use AI agents to fix grammar, validate claims, and polish your drafts before publishing. When your post is ready, `md2wxr` converts it to WXR so you can import it directly into WordPress -- no copy-pasting or manual formatting required.

## Installation

```bash
pip install md2wxr
```

Or install from source:

```bash
git clone https://github.com/LalatenduMohanty/md2wxr.git
cd md2wxr
pip install .
```

## Usage

```bash
# Basic: converts input.md to input.xml
md2wxr input.md

# Specify output file
md2wxr input.md -o output.xml

# Override the post title (default: first H1 heading)
md2wxr input.md --title "My Custom Title"

# Set post status (default: draft)
md2wxr input.md --status publish

# Set author login name (default: admin)
md2wxr input.md --author jdoe

# Set post date (default: today)
md2wxr input.md --date 2026-05-17
```

## How it works

1. Reads the Markdown file
2. Extracts the first `# H1` heading as the post title (or uses `--title`)
3. Converts the remaining Markdown to HTML
4. Wraps the HTML in a valid WXR 1.2 XML structure
5. Writes the output file

The generated XML matches the exact format produced by WordPress's own export function (`export_wp()`), including the comment header block, namespace declarations, author metadata, and CDATA-wrapped content that WordPress.com requires.

## Importing into WordPress

1. Log in to your WordPress site as an administrator
2. Go to **Tools > Import**
3. Under **WordPress**, click **Install Now** (if needed), then **Run Importer**
4. Upload the generated `.xml` file
5. Map the author to an existing user on your site
6. Review and publish the imported post

## License

[Apache License 2.0](LICENSE)
