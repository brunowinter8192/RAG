#!/usr/bin/env python3
"""Clean SearXNG Sphinx docs: remove header nav, footer, inline [docs] markers."""

import re
from pathlib import Path

INPUT_DIR = Path(__file__).parent.parent.parent / "data" / "documents" / "SearXNG_Docs"
OUTPUT_DIR = Path(__file__).parent / "cleaned"

LOGO_PATTERN = re.compile(r'^\[ !\[Logo of ')
DOCS_MARKER_PATTERN = re.compile(r'\[docs\]\[]\(https://docs\.searxng\.org/[^)]*\)\n?')
MULTI_BLANK = re.compile(r'\n{3,}')


def clean_file(content, filename):
    lines = content.split('\n')

    # Extract source comment
    source_line = None
    for line in lines:
        if line.strip().startswith('<!-- source:'):
            source_line = line.strip()
            break

    # Find first real heading
    first_heading_idx = None
    for i, line in enumerate(lines):
        if line.startswith('# '):
            first_heading_idx = i
            break

    # Find logo line (content-end marker)
    logo_idx = None
    for i, line in enumerate(lines):
        if LOGO_PATTERN.match(line):
            logo_idx = i
            break

    # Extract content
    if first_heading_idx is not None and logo_idx is not None:
        content_lines = lines[first_heading_idx:logo_idx]
    elif first_heading_idx is not None:
        content_lines = lines[first_heading_idx:]
    else:
        # No heading found — keep everything before logo
        start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('<!-- source:'):
                start = i + 1
                break
        end = logo_idx if logo_idx else len(lines)
        content_lines = lines[start:end]

    result_parts = []
    if source_line:
        result_parts.append(source_line)
        result_parts.append('')

    result_parts.extend(content_lines)
    result = '\n'.join(result_parts)

    # Remove [docs] markers (inline noise in _modules_ files)
    if filename.startswith('_modules_'):
        result = DOCS_MARKER_PATTERN.sub('', result)

    # Collapse excessive blank lines
    result = MULTI_BLANK.sub('\n\n', result)
    result = result.strip()

    return result


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    md_files = sorted(INPUT_DIR.glob('*.md'))
    total_before = 0
    total_after = 0
    skipped = []

    for md_file in md_files:
        original = md_file.read_text(encoding='utf-8')
        total_before += len(original)

        cleaned = clean_file(original, md_file.name)
        total_after += len(cleaned)

        # Flag files with very little content
        content_only = cleaned
        for line in cleaned.split('\n'):
            if line.strip().startswith('<!-- source:'):
                content_only = content_only.replace(line, '').strip()
                break

        if len(content_only) < 50:
            skipped.append(md_file.name)

        out_path = OUTPUT_DIR / md_file.name
        out_path.write_text(cleaned + '\n', encoding='utf-8')

    reduction = (total_before - total_after) / total_before * 100 if total_before else 0

    print(f"FILES PROCESSED: {len(md_files)}")
    print(f"\nCLEANUP RESULTS:")
    print(f"  Total chars before: {total_before:>10,}")
    print(f"  Total chars after:  {total_after:>10,}")
    print(f"  Reduction:          {reduction:.1f}%")

    if skipped:
        print(f"\nNEARLY EMPTY FILES ({len(skipped)}):")
        for name in skipped:
            print(f"  {name}")


if __name__ == '__main__':
    main()
