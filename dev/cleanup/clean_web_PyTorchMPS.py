"""
Clean up PyTorch docs crawl4ai markdown files.

Site: docs.pytorch.org
Pattern: Large header block (nav, sidebar TOC ~2944 lines) before first # heading,
         followed by footer (rating widget, prev/next nav, PyTorch Libraries, copyright).

Header end marker: Lines "Rate this Page" + "★ ★ ★ ★ ★" just before the first # heading.
Footer start marker: "Rate this Page" after the last content line (post-content rating widget).
"""

import re
from pathlib import Path

INPUT_DIR = Path(__file__).parent.parent.parent / "data" / "documents" / "PyTorchMPS"


def clean_file(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    original_len = len(text)

    lines = text.splitlines()

    # Preserve source comment (always line 0 if present)
    source_comment = ""
    start_scan = 0
    if lines and lines[0].startswith("<!-- source:"):
        source_comment = lines[0]
        start_scan = 1

    # Find first # heading line
    first_heading_idx = None
    for i in range(start_scan, len(lines)):
        if lines[i].startswith("# "):
            first_heading_idx = i
            break

    if first_heading_idx is None:
        # No heading found — keep everything after source comment
        content_lines = lines[start_scan:]
    else:
        # Content starts at first # heading
        content_lines = lines[first_heading_idx:]

    # Find footer start: "Rate this Page" followed by "★ ★ ★ ★ ★"
    # This pattern appears at content end (post-content rating widget).
    # We want to keep the content block, strip from footer marker onward.
    footer_start = None
    i = 0
    while i < len(content_lines):
        line = content_lines[i].strip()
        if line == "Rate this Page":
            # Check if next non-empty line is the star rating
            j = i + 1
            while j < len(content_lines) and content_lines[j].strip() == "":
                j += 1
            if j < len(content_lines) and content_lines[j].strip() == "★ ★ ★ ★ ★":
                footer_start = i
                break
        i += 1

    if footer_start is not None:
        content_lines = content_lines[:footer_start]

    # Strip trailing empty lines
    while content_lines and content_lines[-1].strip() == "":
        content_lines.pop()

    # Also strip "Copy to clipboard" lines that appear after code blocks
    # These are UI elements injected by the site
    content_lines = [
        line for line in content_lines
        if line.strip() != "Copy to clipboard"
    ]

    # Reconstruct
    parts = []
    if source_comment:
        parts.append(source_comment)
        parts.append("")
    parts.extend(content_lines)

    cleaned = "\n".join(parts) + "\n"
    path.write_text(cleaned, encoding="utf-8")

    return original_len, len(cleaned)


def main():
    md_files = sorted(INPUT_DIR.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {INPUT_DIR}")
        return

    total_before = 0
    total_after = 0

    for path in md_files:
        before, after = clean_file(path)
        total_before += before
        total_after += after
        reduction = (before - after) / before * 100 if before > 0 else 0
        print(f"  {path.name[:60]:<60} {before:>8} -> {after:>8} ({reduction:.1f}%)")

    overall = (total_before - total_after) / total_before * 100 if total_before > 0 else 0
    print(f"\nFILES PROCESSED: {len(md_files)}")
    print(f"Total chars before: {total_before:,}")
    print(f"Total chars after:  {total_after:,}")
    print(f"Reduction:          {overall:.1f}%")


if __name__ == "__main__":
    main()
