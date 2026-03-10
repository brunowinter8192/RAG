#!/usr/bin/env python3
"""Analyze Sphinx noise patterns in SearXNG markdown docs."""

import re
import sys
from pathlib import Path

INPUT_DIR = Path(__file__).parent.parent.parent / "data" / "documents" / "SearXNG_Docs"

LOGO_PATTERN = re.compile(r'^\[ !\[Logo of ')
DOCS_MARKER_PATTERN = re.compile(r'\[docs\]\[]\(https://docs\.searxng\.org/')


def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    total_chars = sum(len(l) for l in lines)

    # Find source comment
    has_source = any(l.strip().startswith('<!-- source:') for l in lines)

    # Find first real heading (# Title)
    first_heading_idx = None
    for i, line in enumerate(lines):
        if line.startswith('# '):
            first_heading_idx = i
            break

    # Header noise: lines between source comment and first heading
    header_noise_lines = first_heading_idx if first_heading_idx else 0

    # Find logo line (content-end marker)
    logo_idx = None
    for i, line in enumerate(lines):
        if LOGO_PATTERN.match(line):
            logo_idx = i
            break

    # Footer noise: lines from logo to EOF
    footer_noise_lines = (total_lines - logo_idx) if logo_idx else 0

    # Inline [docs] markers
    docs_markers = sum(1 for l in lines if DOCS_MARKER_PATTERN.search(l))

    # Content lines (between heading and logo)
    if first_heading_idx is not None and logo_idx is not None:
        content_lines = logo_idx - first_heading_idx
    elif first_heading_idx is not None:
        content_lines = total_lines - first_heading_idx
    else:
        content_lines = 0

    # Content chars
    if first_heading_idx is not None and logo_idx is not None:
        content_chars = sum(len(lines[i]) for i in range(first_heading_idx, logo_idx))
    elif first_heading_idx is not None:
        content_chars = sum(len(lines[i]) for i in range(first_heading_idx, total_lines))
    else:
        content_chars = 0

    # Source comment chars (to keep)
    source_chars = 0
    if has_source:
        for l in lines:
            if l.strip().startswith('<!-- source:'):
                source_chars = len(l)
                break

    return {
        'file': filepath.name,
        'total_lines': total_lines,
        'total_chars': total_chars,
        'header_noise_lines': header_noise_lines,
        'footer_noise_lines': footer_noise_lines,
        'content_lines': content_lines,
        'content_chars': content_chars + source_chars,
        'docs_markers': docs_markers,
        'has_source': has_source,
        'has_heading': first_heading_idx is not None,
        'has_footer_marker': logo_idx is not None,
    }


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT_DIR

    if not target.exists():
        print(f"Directory not found: {target}")
        return

    md_files = sorted(target.glob('*.md'))
    if not md_files:
        print(f"No markdown files in {target}")
        return

    results = [analyze_file(f) for f in md_files]

    # Summary
    total_chars = sum(r['total_chars'] for r in results)
    content_chars = sum(r['content_chars'] for r in results)
    noise_chars = total_chars - content_chars
    total_docs_markers = sum(r['docs_markers'] for r in results)
    files_with_docs = sum(1 for r in results if r['docs_markers'] > 0)

    no_footer = [r for r in results if not r['has_footer_marker']]
    no_heading = [r for r in results if not r['has_heading']]
    low_content = [r for r in results if r['content_lines'] < 5]

    print(f"FILES: {len(results)}")
    print(f"\nCHAR ANALYSIS:")
    print(f"  Total:   {total_chars:>10,}")
    print(f"  Content: {content_chars:>10,} ({content_chars/total_chars*100:.1f}%)")
    print(f"  Noise:   {noise_chars:>10,} ({noise_chars/total_chars*100:.1f}%)")
    print(f"  Projected reduction: {noise_chars/total_chars*100:.1f}%")

    print(f"\nINLINE [docs] MARKERS:")
    print(f"  Total markers: {total_docs_markers}")
    print(f"  Files with markers: {files_with_docs}")

    if no_footer:
        print(f"\nFILES WITHOUT FOOTER MARKER ({len(no_footer)}):")
        for r in no_footer:
            print(f"  {r['file']}")

    if no_heading:
        print(f"\nFILES WITHOUT HEADING ({len(no_heading)}):")
        for r in no_heading:
            print(f"  {r['file']}")

    if low_content:
        print(f"\nLOW CONTENT FILES (<5 lines, {len(low_content)}):")
        for r in low_content:
            print(f"  {r['file']} ({r['content_lines']} lines, {r['content_chars']} chars)")

    # Header/Footer noise distribution
    header_lines = [r['header_noise_lines'] for r in results]
    footer_lines = [r['footer_noise_lines'] for r in results]
    print(f"\nHEADER NOISE: min={min(header_lines)}, max={max(header_lines)}, avg={sum(header_lines)/len(header_lines):.1f}")
    print(f"FOOTER NOISE: min={min(footer_lines)}, max={max(footer_lines)}, avg={sum(footer_lines)/len(footer_lines):.1f}")


if __name__ == '__main__':
    main()
