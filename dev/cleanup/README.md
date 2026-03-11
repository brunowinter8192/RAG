# cleanup/ — SearXNG Sphinx Docs Cleaning (v2)

Production cleaning script for SearXNG documentation crawl. Successor to `explore/`.

## Script

**`clean_web_SearXNG_Docs.py`** — Removes Sphinx site chrome from crawled markdown files.

Patterns removed:
- v1: Navigation headers, footer logo blocks, inline `[docs][]` markers
- v2: Heading links (`## [Title](URL)` -> `## Title`), TOC blocks, bare labels, autodoc attributes/methods, `[[source]]` links

Input: `data/documents/SearXNG_Docs/*.md`
Output: `dev/cleanup/cleaned_SearXNG_Docs/` (originals untouched)

## Output

`cleaned_SearXNG_Docs/` — 280 cleaned markdown files ready for chunking and indexing.

## Usage

```bash
./venv/bin/python dev/cleanup/clean_web_SearXNG_Docs.py
```
