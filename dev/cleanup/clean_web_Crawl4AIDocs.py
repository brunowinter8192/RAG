#!/usr/bin/env python3
"""
Cleanup script for Crawl4AI documentation website-crawled markdown files.

Header pattern (lines to remove before first # heading):
- Lines 3-82: Site navigation (top bar + full sidebar nav)
- Line 83: horizontal rule separator
- Lines 84+: In-page TOC with anchor links ending in blank line before # heading

Footer pattern (lines to remove after last content):
- "Page Copy" lines
- Copy as Markdown / View as Markdown / Open in ChatGPT link lines
- "ESC to close" line
- "#### On this page" section (duplicate per-page TOC with anchor links)
- "* * *" separator followed by "> Feedback"
- "##### Search" / "xClose" / "Type to start searching"
- "[ Ask AI ]" link
"""

import re
from pathlib import Path

INPUT_DIR = Path(__file__).parent.parent.parent / "data" / "documents" / "Crawl4AIDocs"
OUTPUT_DIR = Path(__file__).parent / "cleaned_Crawl4AIDocs"


def find_content_start(lines: list[str]) -> int:
    """Find line index of first # heading (actual content start)."""
    for i, line in enumerate(lines):
        if line.startswith("# ") or line.startswith("#  "):
            return i
    return 0


def find_content_end(lines: list[str]) -> int:
    """Find line index where footer begins (exclusive end of content).

    Footer start markers (forward scan from content start):
    1. "Page Copy" standalone line — appears first in most files
    2. "* * *" followed by "> Feedback" — fallback for files without "Page Copy"
    """
    n = len(lines)

    for i in range(n):
        stripped = lines[i].strip()

        if stripped == "Page Copy":
            return i

        if stripped == "* * *" and i + 1 < n and lines[i + 1].strip().startswith("> Feedback"):
            return i

    return n


def clean_file(content: str) -> str:
    """Remove header navigation and footer chrome from crawled markdown."""
    lines = content.splitlines(keepends=True)

    # Preserve source comment on line 1 if present
    source_comment = ""
    start_idx = 0
    if lines and lines[0].strip().startswith("<!-- source:"):
        source_comment = lines[0]
        start_idx = 1

    content_lines = lines[start_idx:]

    content_start = find_content_start(content_lines)
    content_end = find_content_end(content_lines)

    cleaned_lines = content_lines[content_start:content_end]

    # Remove standalone "Copy" lines (copy-to-clipboard button artifacts after code blocks)
    cleaned_lines = [
        line for line in cleaned_lines
        if line.rstrip("\n") != "Copy"
    ]

    # Strip trailing blank lines from the cleaned section
    while cleaned_lines and cleaned_lines[-1].strip() == "":
        cleaned_lines.pop()

    result = source_comment
    if cleaned_lines:
        result += "\n"
        result += "".join(cleaned_lines)
        result += "\n"

    return result


def process_all_files():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    md_files = sorted(INPUT_DIR.glob("*.md"))
    total_before = 0
    total_after = 0
    processed = 0

    for md_file in md_files:
        original = md_file.read_text(encoding="utf-8")
        cleaned = clean_file(original)

        out_path = OUTPUT_DIR / md_file.name
        out_path.write_text(cleaned, encoding="utf-8")

        before = len(original)
        after = len(cleaned)
        total_before += before
        total_after += after
        processed += 1

        reduction = (before - after) / before * 100 if before > 0 else 0
        print(f"  {md_file.name}: {before} -> {after} chars ({reduction:.1f}% reduction)")

    total_reduction = (total_before - total_after) / total_before * 100 if total_before > 0 else 0
    print(f"\nFILES PROCESSED: {processed}")
    print(f"Total chars before: {total_before:,}")
    print(f"Total chars after:  {total_after:,}")
    print(f"Reduction: {total_reduction:.1f}%")


if __name__ == "__main__":
    process_all_files()
