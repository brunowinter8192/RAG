# Chunking Strategy Evaluation Plan

## 1. Current State

### Chunker Architecture (`src/rag/chunker.py`)

**Entry point:** `chunk_workflow(file_path, chunk_size=1000, overlap=200)`

**Pipeline:**
1. `load_file()` — reads raw text
2. `chunk_semantic()` — splits using hierarchical separators, then merges
3. `enrich_chunks()` — wraps in `{content, source, index, total_chunks}` dicts

**Splitting logic (`chunk_semantic`, line 40):**
- Separators (in priority order): `["\n\n", "\n", ". ", "! ", "? ", " "]`
- `recursive_split()` (line 47): tries each separator in turn; if a part still exceeds chunk_size, falls back to the next separator; last resort is hard character split at chunk_size boundary
- `merge_with_overlap()` (line 85): accumulates splits into chunks up to chunk_size, then starts a new chunk using word-aligned overlap from the end of the previous chunk (`get_word_aligned_overlap()`, line 74)

**Current defaults:**
- `DEFAULT_CHUNK_SIZE = 1000` (characters)
- `DEFAULT_OVERLAP = 200` (characters, ~20%)

**Missing features vs. common alternatives:**
- No markdown-aware separators (`#`, `##`, `---`, ` ``` `) — headers and code blocks treated as normal text
- No sentence-level splitter (NLTK/spacy)
- Overlap is character-based, word-aligned only at the start of the overlap region

---

## 2. Paper Findings

### Pipeline_Optimization_Paper — Chunking Strategy Comparison

**Source:** TABLE II (chunk_index 20), Summary Section (chunk_index 21, 29)

| Chunking Strategy | Index | Acc@3 | NDCG@3 | Acc@5 | NDCG@5 | Acc@10 | NDCG@10 |
|---|---|---|---|---|---|---|---|
| 2000 chars recursive | HNSW | 0.412 | 0.356 | 0.462 | 0.378 | 0.522 | 0.396 |
| 512 chars recursive | HNSW | **0.460** | **0.415** | **0.500** | **0.431** | **0.544** | **0.445** |
| 512 chars recursive | IVF-Flat | 0.427 | 0.388 | 0.461 | 0.402 | 0.498 | 0.414 |
| Semantic (variable) | HNSW | 0.456 | 0.404 | 0.501 | 0.422 | 0.553 | 0.439 |

**Key numbers:**
- 512 chars vs. 2000 chars: **+4.8pp Acc@3** (0.412 → 0.460), **+5.9pp NDCG@3** (0.356 → 0.415)
- Semantic chunking ≈ 512-char (Acc@3 0.456 vs. 0.460), slight edge on Acc@10 (0.553 vs. 0.544)
- Reranking compensates ~half the gap: 2000-char + reranker → Acc@3 ≈ 0.506 (chunk_index 28)
- HNSW > IVF-Flat for same chunking (0.460 vs. 0.427, +3.3pp)

**Explanation (chunk_index 29):** Smaller chunks reduce semantic noise, improve query-passage alignment, and enable more precise relevance judgments.

**Our position:** At 1000 chars we are between the two tested extremes. The paper does not test 500, 750, or 1000 chars — our eval fills this gap.

### Qwen3_Embedding_Paper — Sequence Length

**Source:** TABLE 1 (chunk_index 13), Architecture Section (chunk_index 12)

- All three Qwen3-Embedding sizes (0.6B, 4B, 8B) have **max sequence length = 32K tokens**
- Documents are passed **unchanged** (no instruction prefix); instruction prefix is prepended only to queries
- No hard truncation below 32K mentioned; practical limit is VRAM when running locally via llama-server

**Implication for chunking:** Qwen3-Embedding has no technical reason to prefer small chunks from a context-window perspective. The 32K limit is far above any practical chunk size we would use (500–1500 chars ≈ 100–400 tokens). The benefit of smaller chunks is purely retrieval-quality / query-alignment — not model constraint.

---

## 3. What To Test

### Chunk Size Variants

| Variant | chunk_size | overlap | separator_set | Notes |
|---|---|---|---|---|
| A | 500 | 100 | default | Below paper's 512-char optimum (apples-to-apples comparison) |
| B | 750 | 150 | default | Midpoint between paper extremes; not tested in paper |
| C | 1000 | 200 | default | **Current baseline** |
| D | 1500 | 300 | default | Between current and paper's 2000-char underperformer |
| E | 500 | 100 | markdown-aware | Same size as A, adds `#`, `##`, `---`, ` ``` ` separators |
| F | 750 | 150 | markdown-aware | Same size as B, markdown-aware |

**Rationale for overlap = chunk_size / 5:** Keeps overlap ratio constant at 20% across all variants, matching the current default ratio.

**Markdown-aware variants (E, F):** Target structured documents (SearXNG_Docs dataset contains markdown). For plain-text corpora these will behave identically to A/B.

### Datasets

Both existing datasets are used for all variants:

| Dataset | File | Corpus source | Notes |
|---|---|---|---|
| `qwen3_paper` | `datasets/qwen3_paper.json` | `source_json` (pre-chunked JSON) | Scientific paper, dense prose |
| `searxng_docs` | `datasets/searxng_docs.json` | `corpus_from_db` (live DB) | Markdown docs, structural variety |

**Note:** `searxng_docs` uses `corpus_from_db` — the corpus is whatever is currently indexed in the DB. To test a different chunk size, a new corpus must be re-chunked and re-indexed. See Section 5.

### Retrievers

Run `--hybrid-sweep` for each variant (Dense + Sparse + Hybrid side by side). Primary metric: **NDCG@3**.

### Metrics

Standard eval suite metrics (from `eval_config.py`):
- NDCG @ [3, 5, 10]
- Recall @ [3, 5, 10]
- P @ [3, 5, 10]

---

## 4. How To Test

### Command Pattern

For each chunk variant, run from project root:

```bash
# Single retriever
./venv/bin/python dev/retrieval_eval/eval_runner.py \
    --dataset <dataset_name> \
    --retriever dense \
    > /tmp/eval_output.md 2>&1

# Full sweep (Dense + Sparse + Hybrid)
./venv/bin/python dev/retrieval_eval/eval_runner.py \
    --dataset <dataset_name> \
    --hybrid-sweep \
    > /tmp/eval_output.md 2>&1
```

### Evaluation Loop

```
for variant in [A, B, C, D, E, F]:
    1. Re-chunk corpus with new chunk_size/separators (see Section 5)
    2. For qwen3_paper: re-generate source_json with new chunks (chunk_workflow)
    3. For searxng_docs: re-index DB collection under new collection name
    4. Run: eval_runner.py --dataset <variant_dataset> --hybrid-sweep
    5. Results auto-saved to: dev/retrieval_eval/results/<dataset>_<retriever>.json
    6. Collect NDCG@3, NDCG@5, NDCG@10 per retriever
```

### Naming Convention for Variant Datasets

| Variant | Dataset name suffix |
|---|---|
| A (500 chars, default) | `_c500` |
| B (750 chars, default) | `_c750` |
| C (1000 chars, default) | `_c1000` (current baseline) |
| D (1500 chars, default) | `_c1500` |
| E (500 chars, markdown) | `_c500_md` |
| F (750 chars, markdown) | `_c750_md` |

Example: `searxng_docs_c500`, `qwen3_paper_c750_md`

---

## 5. Implementation Notes

### What Needs to Change in `chunker.py` for Each Variant

**Variants A–D (different chunk_size, default separators):**

No code changes needed. `chunk_workflow` accepts `chunk_size` and `overlap` as arguments:

```python
# chunk_semantic → recursive_split → merge_with_overlap use the passed-in values
chunks = chunk_workflow(file_path, chunk_size=500, overlap=100)   # Variant A
chunks = chunk_workflow(file_path, chunk_size=750, overlap=150)   # Variant B
chunks = chunk_workflow(file_path, chunk_size=1500, overlap=300)  # Variant D
```

Call `chunk_workflow` with the target size when building the eval corpus — no changes to the source file.

**Variants E–F (markdown-aware separators):**

`chunk_semantic()` at line 40 hardcodes the separator list. To add markdown-aware splitting, a new separator list must be passed through. Currently the function signature does not accept custom separators:

```python
# Current (line 40–43)
def chunk_semantic(content: str, chunk_size: int, overlap: int) -> list[str]:
    separators = ["\n\n", "\n", ". ", "! ", "? ", " "]
    ...
```

**Required change** (scope-limited, only for eval corpus generation — do NOT modify production code):
Create a standalone helper script in `dev/retrieval_eval/` that overrides the separator list and calls `recursive_split` + `merge_with_overlap` directly:

```python
# dev/retrieval_eval/chunk_variants.py  (new file, eval-only)
from src.rag.chunker import recursive_split, merge_with_overlap, load_file, enrich_chunks

MARKDOWN_SEPARATORS = ["# ", "## ", "### ", "\n---\n", "```\n", "\n\n", "\n", ". ", " "]

def chunk_markdown(file_path, chunk_size, overlap):
    content = load_file(file_path)
    splits = recursive_split(content, MARKDOWN_SEPARATORS, chunk_size)
    chunks = merge_with_overlap(splits, chunk_size, overlap)
    return enrich_chunks(chunks, file_path)
```

This avoids modifying `src/rag/chunker.py` and keeps eval tooling in `dev/`.

### Corpus Preparation for `qwen3_paper` Variants

The `qwen3_paper` dataset uses `source_json` (pre-chunked JSON file). To test a new chunk size:
1. Re-run chunking on the original paper PDF/MD source with new parameters
2. Save the output as a new JSON file (matching the `{chunks: [...], document: "..."}` schema that `load_dataset` reads)
3. Point a new dataset JSON to the new source_json path

### Corpus Preparation for `searxng_docs` Variants

The `searxng_docs` dataset uses `corpus_from_db` — it loads live from the DB. To test a different chunk size:
1. Re-index the SearXNG docs under a new collection name (e.g., `SearXNG_Docs_c500`)
2. Create a new dataset JSON: `{"corpus_from_db": true, "collection": "SearXNG_Docs_c500", "queries": {...}, "qrels": {...}}`
3. The queries and qrels from `searxng_docs.json` can be reused (they are query-text based, not chunk-index based)

### Expected Outcome

Based on paper data, we predict:
- Variants A/B will outperform baseline C on NDCG@3 (smaller = better query alignment)
- Variant D will underperform C (approaching the 2000-char underperformer)
- Variants E/F: unclear — depends on how structured the corpus is; markdown-aware splitting should help on `searxng_docs`, negligible on `qwen3_paper`
- Hybrid retriever is expected to benefit most from smaller chunks (SPLADE token overlap increases with focused chunks)
