#!/usr/bin/env python3
import re
from pathlib import Path

PATTERNS = {
    'navigation_header': r'^### Navigation\n',
    'toc_header': r'^### \[Table of Contents\]',
    'project_links': r'^### Project Links\n',
    'quick_search': r'^### Quick search\n',
    'this_page': r'^### This Page\n',
    'copyright_footer': r'^© Copyright',
}


def clean_markdown_file(content: str) -> str:
    lines = content.split('\n')
    output = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # 1. Keep source comment
        if line.startswith('<!-- source:'):
            output.append(line)
            i += 1
            continue

        # 2. Skip ### Navigation block
        if line.strip() == '### Navigation':
            while i < len(lines) and not (lines[i].startswith('# ') or
                                          lines[i].strip().startswith('### ')):
                i += 1
            continue

        # 3. Skip ### [Table of Contents] blocks (redundant)
        if '### [Table of Contents]' in line or line.strip() == '### [Table of Contents]':
            while i < len(lines) and not (lines[i].startswith('# ') or
                                          (lines[i].strip().startswith('### ') and
                                           'Table of Contents' not in lines[i])):
                i += 1
            continue

        # 4. Skip ### Project Links
        if line.strip() == '### Project Links':
            while i < len(lines) and not (lines[i].startswith('# ') or
                                          (lines[i].strip().startswith('### ') and
                                           'Project Links' not in lines[i])):
                i += 1
            continue

        # 5. Skip ### Quick search and ### This Page
        if line.strip() in ['### Quick search', '### This Page']:
            while i < len(lines) and not (lines[i].startswith('# ') or
                                          (lines[i].strip().startswith('### ') and
                                           line.strip() not in lines[i])):
                i += 1
            continue

        # 6. Stop at copyright footer
        if line.strip().startswith('© Copyright'):
            break

        # Add content lines
        output.append(line)
        i += 1

    # Join and clean up excessive blank lines
    result = '\n'.join(output)
    result = re.sub(r'\n\n\n+', '\n\n', result)
    result = result.strip()

    return result


def process_directory(directory: str) -> dict:
    path = Path(directory)

    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    md_files = sorted(path.glob('*.md'))

    if not md_files:
        print(f"No markdown files found in {directory}")
        return {'files': 0, 'total_before': 0, 'total_after': 0}

    total_before = 0
    total_after = 0

    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            original = f.read()

        total_before += len(original)
        cleaned = clean_markdown_file(original)
        total_after += len(cleaned)

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(cleaned)

    return {
        'files': len(md_files),
        'total_before': total_before,
        'total_after': total_after
    }


if __name__ == '__main__':
    input_dir = '/Users/brunowinter2000/Documents/ai/Meta/ClaudeCode/MCP/RAG/data/documents/SearXNG_Docs'

    stats = process_directory(input_dir)

    reduction = ((stats['total_before'] - stats['total_after']) / stats['total_before'] * 100) \
        if stats['total_before'] > 0 else 0

    print(f"FILES PROCESSED: {stats['files']}")
    print(f"\nCLEANUP RESULTS:")
    print(f"- Total chars before: {stats['total_before']}")
    print(f"- Total chars after: {stats['total_after']}")
    print(f"- Reduction: {reduction:.1f}%")
