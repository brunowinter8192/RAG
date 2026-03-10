"""
Cleanup script for SearXNG Sphinx documentation crawl (v2).

Removes Sphinx site chrome from all .md files in SearXNG_Docs/:
  v1:
  - HEADER: ### Navigation block between <!-- source: --> comment and first # heading
  - FOOTER: Everything from "[ ![Logo of SearXNG]" line to EOF
  - INLINE: [docs][](URL) markers in _modules_* files
  v2:
  - HEADING_LINKS: ## [Title](URL) -> ## Title
  - TOC_BLOCKS: Groups of internal anchor links (docs.searxng.org/...#...)
  - BARE_LABELS: "info" -> "> **Info:**", "further read" -> "**Further reading:**"
  - AUTODOC: searx.engines.foo.bar _= 'val'_ -> clean attribute docs
  - SOURCE_LINKS: [[source]](URL) markers in autodoc

Output: dev/cleanup/cleaned_SearXNG_Docs/ (originals untouched)
"""

import re
import sys
from pathlib import Path

INPUT_DIR = Path(__file__).parent.parent.parent / "data" / "documents" / "SearXNG_Docs"
OUTPUT_DIR = Path(__file__).parent / "cleaned_SearXNG_Docs"

FOOTER_MARKER = "[ ![Logo of SearXNG]"
DOCS_INLINE_PATTERN = re.compile(r'\[docs\]\[\]\(https?://[^\)]+\)\n?')

# v2: ## [Title](URL) or ###  [Title](URL) -> ## Title
HEADING_LINK_PATTERN = re.compile(r'^(#{1,6})\s+\[([^\]]+)\]\(https?://[^\)]+\)\s*$', re.MULTILINE)

# v2: TOC blocks — consecutive lines of "  * [Text](https://docs.searxng.org/...#...)"
TOC_BLOCK_PATTERN = re.compile(
    r'(?:^[ \t]*\*\s+\[[^\]]+\]\(https://docs\.searxng\.org/[^\)]*#[^\)]*\)\s*\n){2,}',
    re.MULTILINE
)

# v2: bare labels on their own line
BARE_INFO_PATTERN = re.compile(r'^info$', re.MULTILINE)
BARE_FURTHER_READ_PATTERN = re.compile(r'^further read$', re.MULTILINE)

# v2: autodoc attribute: searx.engines.foo.bar _= 'val'_ -> **foo.bar** = `'val'`
AUTODOC_ATTR_PATTERN = re.compile(
    r'^(searx\.\w+(?:\.\w+)+)\s+_(?::.*?)?=\s*(.+?)_\s*$',
    re.MULTILINE
)

# v2: autodoc method: searx.engines.foo.bar()[[source]](URL) -> **foo.bar()**
AUTODOC_METHOD_PATTERN = re.compile(
    r'^(searx\.\w+(?:\.\w+)+\([^)]*\))\[?\[?source\]?\]?\(https?://[^\)]+\)\s*$',
    re.MULTILINE
)

# v2: [[source]](URL) standalone markers
SOURCE_LINK_PATTERN = re.compile(r'\[\[source\]\]\(https?://[^\)]+\)')


# v1 functions (unchanged)

def clean_header(text: str) -> str:
    source_comment_end = text.find("\n", text.find("<!-- source:"))
    if source_comment_end == -1:
        return text

    after_comment = text[source_comment_end + 1:]

    nav_match = re.match(r'\n*### Navigation\n(?:.*\n)*?(?=\n*#[^#])', after_comment)
    if nav_match:
        content_start = source_comment_end + 1 + nav_match.end()
        return text[:source_comment_end + 1] + "\n" + text[content_start:].lstrip("\n")

    return text


def clean_footer(text: str) -> str:
    idx = text.find(FOOTER_MARKER)
    if idx == -1:
        return text

    line_start = text.rfind("\n", 0, idx)
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1

    return text[:line_start].rstrip("\n") + "\n"


def clean_inline_docs_markers(text: str) -> str:
    return DOCS_INLINE_PATTERN.sub("", text)


# v2 functions

def clean_heading_links(text: str) -> str:
    return HEADING_LINK_PATTERN.sub(r'\1 \2', text)


def clean_toc_blocks(text: str) -> str:
    return TOC_BLOCK_PATTERN.sub('', text)


def clean_bare_labels(text: str) -> str:
    text = BARE_INFO_PATTERN.sub('> **Info:**', text)
    text = BARE_FURTHER_READ_PATTERN.sub('**Further reading:**', text)
    return text


def clean_autodoc(text: str) -> str:
    def replace_attr(m):
        full_name = m.group(1)
        short_name = full_name.split('searx.')[-1]
        value = m.group(2).strip()
        return f"**{short_name}** = `{value}`"

    text = AUTODOC_ATTR_PATTERN.sub(replace_attr, text)

    def replace_method(m):
        full_name = m.group(1)
        short_name = full_name.split('searx.')[-1]
        return f"**{short_name}**"

    text = AUTODOC_METHOD_PATTERN.sub(replace_method, text)
    text = SOURCE_LINK_PATTERN.sub('', text)
    return text


def clean_file(src: Path, dst: Path) -> tuple[int, int]:
    text = src.read_text(encoding="utf-8")
    chars_before = len(text)

    # v1
    text = clean_header(text)
    text = clean_footer(text)
    if src.name.startswith("_modules_"):
        text = clean_inline_docs_markers(text)

    # v2
    text = clean_heading_links(text)
    text = clean_toc_blocks(text)
    text = clean_bare_labels(text)
    text = clean_autodoc(text)

    # normalize multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    dst.write_text(text, encoding="utf-8")
    return chars_before, len(text)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(INPUT_DIR.glob("*.md"))
    if not files:
        print(f"No .md files found in {INPUT_DIR}")
        sys.exit(1)

    total_before = 0
    total_after = 0
    counters = {
        "header_nav": 0, "footer_logo": 0, "inline_docs": 0,
        "heading_links": 0, "toc_blocks": 0, "bare_labels": 0, "autodoc": 0
    }

    for src in files:
        dst = OUTPUT_DIR / src.name
        raw = src.read_text(encoding="utf-8")

        if "### Navigation" in raw and "<!-- source:" in raw:
            counters["header_nav"] += 1
        if FOOTER_MARKER in raw:
            counters["footer_logo"] += 1
        if src.name.startswith("_modules_") and DOCS_INLINE_PATTERN.search(raw):
            counters["inline_docs"] += 1
        if HEADING_LINK_PATTERN.search(raw):
            counters["heading_links"] += 1
        if TOC_BLOCK_PATTERN.search(raw):
            counters["toc_blocks"] += 1
        if BARE_INFO_PATTERN.search(raw) or BARE_FURTHER_READ_PATTERN.search(raw):
            counters["bare_labels"] += 1
        if AUTODOC_ATTR_PATTERN.search(raw) or AUTODOC_METHOD_PATTERN.search(raw):
            counters["autodoc"] += 1

        before, after = clean_file(src, dst)
        total_before += before
        total_after += after

    reduction = (1 - total_after / total_before) * 100 if total_before else 0

    print(f"FILES PROCESSED: {len(files)}")
    print()
    print("PATTERNS DETECTED:")
    for name, count in counters.items():
        print(f"  - {name}: {count}/{len(files)}")
    print()
    print("CLEANUP RESULTS:")
    print(f"  - Total chars before: {total_before:,}")
    print(f"  - Total chars after:  {total_after:,}")
    print(f"  - Reduction: {reduction:.1f}%")
    print()
    print(f"OUTPUT: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
