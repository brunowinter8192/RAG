# dev/cleanup/ — Web Markdown Cleanup Scripts

Per-collection cleanup scripts for website-crawled markdown files. Each script removes site-specific navigation, cookie banners, headers, and footers while preserving content.

---

## clean_web_RAG_MCP.py

**Purpose:** Clean website-crawled markdown files in `data/documents/RAG_MCP/`. Removes site chrome from 14 different domains (anthropic.com, together.ai, weaviate.io, crunchydata.com, pinecone.io, etc.). Skips `arxiv__*.md` files (PDF-converted papers, not web crawls).
**Input:** `data/documents/RAG_MCP/*.md` (in-place overwrite).
**Output:** Cleaned files written back to `data/documents/RAG_MCP/` with navigation, cookie banners, and footers removed. 404/error pages replaced with a `<!-- NOTE: ... -->` marker.

**Usage:**
```bash
./venv/bin/python dev/cleanup/clean_web_RAG_MCP.py
```

---

## clean_web_SearXNG_Docs.py

**Purpose:** Clean Sphinx site chrome from SearXNG documentation crawl (v2). Two-pass: v1 removes navigation headers and footer logo blocks; v2 removes heading links, TOC blocks, bare labels, autodoc attributes/methods, and `[[source]]` links.
**Input:** `data/documents/SearXNG_Docs/*.md` (read-only, originals untouched).
**Output:** Cleaned files written to `dev/cleanup/cleaned_SearXNG_Docs/` (280 files).

**Usage:**
```bash
./venv/bin/python dev/cleanup/clean_web_SearXNG_Docs.py
```

---

## clean_web_Crawl4AIDocs.py

**Purpose:** Clean Crawl4AI documentation website markdown files. Removes header navigation (site nav + in-page TOC), footer chrome (copy buttons, "Page Copy" markers, feedback sections, prev/next nav), and standalone "Copy" lines.
**Input:** `data/documents/Crawl4AIDocs/*.md` (read-only, originals untouched).
**Output:** Cleaned files written to `dev/cleanup/cleaned_Crawl4AIDocs/`.

**Usage:**
```bash
./venv/bin/python dev/cleanup/clean_web_Crawl4AIDocs.py
```

---

## clean_web_challange.py

**Purpose:** Clean markdown files from HuggingFace (model pages, docs pages) and Gradio documentation. Dispatches to site-specific cleaners based on filename prefix (`huggingface.co_*` vs `www.gradio.app_*`).
**Input:** `data/documents/challange/*.md` (in-place overwrite).
**Output:** Cleaned files written back in-place. HF model pages: removes logo, nav, TOC, tags, footer. HF docs: removes sidebar, version selector, prev/next nav. Gradio: removes full sidebar nav, prev/next, related guides.

**Usage:**
```bash
./venv/bin/python dev/cleanup/clean_web_challange.py
```

---

## clean_web_PyTorchMPS.py

**Purpose:** Clean PyTorch documentation markdown files (docs.pytorch.org). Removes large header block (~2944 lines of nav/sidebar TOC) before first `# ` heading and footer (rating widget, prev/next nav, copyright).
**Input:** `data/documents/PyTorchMPS/*.md` (in-place overwrite).
**Output:** Cleaned files written back in-place with header and footer stripped.

**Usage:**
```bash
./venv/bin/python dev/cleanup/clean_web_PyTorchMPS.py
```

---

## clean_web_searxng.py

**Purpose:** Clean docs.searxng.org Sphinx docs crawled via Crawl4AI. Reduces excess blank lines after `<!-- source: -->` comments and removes rare Sphinx navigation blocks (`### Navigation` + breadcrumb links).
**Input:** `data/documents/searxng/searxng__*.md` (in-place overwrite).
**Output:** Cleaned files written back in-place. Typically 271 files processed.

**Usage:**
```bash
./venv/bin/python dev/cleanup/clean_web_searxng.py
```
