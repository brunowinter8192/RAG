# explore/ — Pattern Analysis & Initial Cleaning (v1)

Predecessor to `cleanup/`. Used for analyzing noise patterns in SearXNG crawl data and building the first cleaning prototype.

## Scripts

**`analyze_patterns.py`** — Analyzes Sphinx noise patterns (header/footer/inline markers) across all markdown files. Reports char counts, noise ratios, and edge cases (missing footers, empty files).

```bash
./venv/bin/python dev/explore/analyze_patterns.py [optional_input_dir]
```

**`clean_searxng.py`** — v1 cleaning (header nav, footer logo, inline `[docs]` markers only). Output in `cleaned/`.

```bash
./venv/bin/python dev/explore/clean_searxng.py
```

## Note

For production cleaning, use `cleanup/clean_web_SearXNG_Docs.py` (v2) which handles additional patterns.
