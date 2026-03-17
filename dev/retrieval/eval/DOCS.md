# dev/retrieval/eval/ — Retrieval Evaluation Suite

BEIR-format evaluation suite measuring retrieval quality with `pytrec_eval` metrics (NDCG, Recall, Precision at k=3, 5, 10).

---

## eval_runner.py

**Purpose:** Run retrieval evaluation on a named dataset using one of three retriever types (dense, sparse, hybrid). Supports MRL dimension sweeps and side-by-side comparisons.
**Input:** Dataset name (looks up `datasets/<name>.json`), retriever type, and optional sweep flags.
**Output:** Metric table (stdout) + JSON result file in `results/<dataset>_<retriever>.json`.

**CLI flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--dataset` | required | Dataset name (without `.json`), from `datasets/` |
| `--retriever` | `dense` | `dense`, `sparse`, or `hybrid` |
| `--top-k` | 10 | Number of results to retrieve |
| `--truncate-dims` | None | MRL dimension truncation (dense only) |
| `--rrf-k` | 60 | RRF k parameter for hybrid fusion |
| `--mrl-sweep` | off | Run dense across dims 256, 512, 1024, 2048, full |
| `--hybrid-sweep` | off | Run dense + sparse + hybrid side-by-side |

**Usage:**
```bash
# Single retriever
./venv/bin/python dev/retrieval/eval/eval_runner.py \
    --dataset searxng_docs --retriever dense --top-k 10

# MRL dimension sweep (dense only)
./venv/bin/python dev/retrieval/eval/eval_runner.py \
    --dataset qwen3_paper --mrl-sweep

# Dense vs Sparse vs Hybrid side-by-side
./venv/bin/python dev/retrieval/eval/eval_runner.py \
    --dataset searxng_docs --hybrid-sweep --rrf-k 60
```

**Dataset format** (`datasets/*.json`):
```json
{
  "queries": {"q1": "What is X?"},
  "qrels": {"q1": {"chunk_0": 1}},
  "corpus": {"chunk_0": {"text": "...", "document": "doc.md"}},
  "corpus_from_db": true,
  "collection": "collection_name"
}
```

If `corpus` is absent and `corpus_from_db: true`, corpus is loaded from PostgreSQL for the named collection. If `source_json` is set, corpus is built from a `chunks.json` file.

---

## eval_config.py

**Purpose:** Shared constants for the evaluation suite (metric names, K values, directory paths).
**Input:** Imported by `eval_runner.py` and retriever modules.
**Output:** Constants `K_VALUES`, `METRICS`, `DATASETS_DIR`, `RESULTS_DIR`.

---

## retrievers/base.py

**Purpose:** Abstract base class defining the BEIR-compatible retriever interface.
**Input:** `corpus` dict, `queries` dict, `top_k` int.
**Output:** `dict[str, dict[str, float]]` — `{query_id: {doc_id: score}}`.

---

## retrievers/dense.py

**Purpose:** Dense retriever using Qwen3-Embedding-8B via llama-server (port 8081). Supports optional MRL dimension truncation.
**Input:** Corpus and query dicts. Optional `truncate_dims` (int) for MRL, optional `query_prefix` (uses Qwen3 instruct format by default).
**Output:** BEIR-format results dict `{query_id: {doc_id: cosine_similarity}}`.

Embeds corpus in batches of 32, applies prefix to queries only. Truncates and re-normalizes vectors if `truncate_dims` is set.

---

## retrievers/sparse.py

**Purpose:** Sparse retriever using SPLADE++ via splade_server (port 8083). Computes sparse cosine similarity between query and corpus vectors.
**Input:** Corpus and query dicts.
**Output:** BEIR-format results dict `{query_id: {doc_id: sparse_cosine_score}}`.

Batches corpus embedding in groups of 32. Similarity computed as dot product of sparse dicts divided by L2 norms.

---

## retrievers/hybrid.py

**Purpose:** Hybrid retriever fusing dense and sparse results with Reciprocal Rank Fusion (RRF).
**Input:** `DenseRetriever` and `SparseRetriever` instances, `rrf_k` parameter (default 60).
**Output:** BEIR-format results dict with RRF-fused scores `{query_id: {doc_id: rrf_score}}`.

RRF formula: `score = Σ 1/(k + rank)` summed across both result lists. Documents appearing in both lists are boosted.
