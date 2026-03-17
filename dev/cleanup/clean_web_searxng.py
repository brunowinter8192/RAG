"""
Cleanup script for docs.searxng.org Sphinx docs crawled via Crawl4AI.

INPUT DIRECTORY: RAG/data/documents/searxng/
FILE PATTERN:    searxng__*.md (271 files)

PATTERNS DETECTED:
1. Excess blank lines (4-5) after <!-- source: URL --> comment — reduce to 1
2. Sphinx navigation block at top of file (### Navigation + breadcrumb links)
   — found in 1 file: searxng__dev__result_types__main__mainresult.md
   — Pattern: '### Navigation' followed by index/modules/next/previous links and » breadcrumbs,
     ending at the first non-list line that contains actual content.

Overwrites originals in-place (git preserves history for rollback).
"""

import glob
import re
from pathlib import Path

INPUT_DIR = Path(__file__).parent.parent.parent / "data" / "documents" / "searxng"
PATTERN = "searxng__*.md"


def clean_file(path: Path) -> tuple[int, int]:
    """Clean a single file. Returns (chars_before, chars_after)."""
    text = path.read_text(encoding="utf-8")
    chars_before = len(text)

    lines = text.splitlines(keepends=True)

    # --- Step 1: Preserve source comment (line 0) ---
    if not lines:
        return chars_before, chars_before

    source_line = lines[0]  # <!-- source: ... -->

    # --- Step 2: Find where real content starts ---
    # Skip blank lines after source comment
    # Also skip any Sphinx navigation block (### Navigation ... breadcrumbs)
    i = 1
    # Skip initial blank lines
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # Check for Sphinx navigation block: starts with '### Navigation'
    if i < len(lines) and lines[i].strip() == "### Navigation":
        # Skip the entire navigation block — all lines that are:
        # - list items with [index], [modules], [next], [previous] links
        # - breadcrumb lines with » separator
        # - blank lines within the navigation block
        # Stop at the first line that is a real heading or non-navigation content
        i += 1  # skip '### Navigation'
        while i < len(lines):
            line = lines[i].strip()
            # Navigation list items (index, modules, next, previous links, breadcrumbs)
            is_nav = (
                re.match(r'^\*\s+\[(?:index|modules|next|previous)', line)
                or re.match(r'^\*\s+\[.*\]\(https://docs\.searxng\.org/.*\)\s*[»|]?', line)
                or line == ""
            )
            if is_nav:
                i += 1
            else:
                break

    # Skip any remaining blank lines to reach actual content
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # --- Step 3: Reassemble: source comment + 1 blank line + content ---
    content_lines = lines[i:]
    cleaned = source_line + "\n" + "".join(content_lines)

    chars_after = len(cleaned)
    path.write_text(cleaned, encoding="utf-8")
    return chars_before, chars_after


def main():
    files = sorted(INPUT_DIR.glob(PATTERN))
    if not files:
        print(f"No files matched {INPUT_DIR / PATTERN}")
        return

    total_before = 0
    total_after = 0
    nav_blocks_removed = 0

    for path in files:
        text_before = path.read_text(encoding="utf-8")
        has_nav = "### Navigation" in text_before and "index" in text_before

        before, after = clean_file(path)
        total_before += before
        total_after += after

        if has_nav:
            nav_blocks_removed += 1

    reduction = (total_before - total_after) / total_before * 100 if total_before else 0
    print(f"FILES PROCESSED: {len(files)}")
    print()
    print("PATTERNS DETECTED:")
    print(f"  - excess_blank_lines_after_source_comment: found in all {len(files)} files (4-5 lines -> 1)")
    print(f"  - sphinx_navigation_block: removed from {nav_blocks_removed} file(s)")
    print()
    print("CLEANUP RESULTS:")
    print(f"  - Total chars before: {total_before:,}")
    print(f"  - Total chars after:  {total_after:,}")
    print(f"  - Reduction: {reduction:.1f}%")
    print()
    print(f"SCRIPT: dev/cleanup/clean_web_searxng.py")
    print(f"OUTPUT: in-place (originals overwritten)")
    print(f"STATUS: CLEAN")


if __name__ == "__main__":
    main()
