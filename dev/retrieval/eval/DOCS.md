# dev/retrieval/eval/ — Retrieval Evaluation Suite

BEIR-format evaluation suite measuring retrieval quality with `pytrec_eval` metrics (NDCG, Recall, Precision at k=3, 5, 10).

---

## eval_runner.py

**Purpose:** Run retrieval evaluation on a named dataset using one of three retriever types (dense, sparse, hybrid). Supports MRL dimension sweeps, reranker evaluation, and side-by-side comparisons.
**Input:** Dataset name (looks up `datasets/<name>.json`), retriever type, and optional sweep flags.
**Output:** Metric table (stdout) + JSON result file in `results/<dataset>_<retriever>.json`.

**DB-backed embeddings:** When a dataset has `corpus_from_db: true`, corpus embeddings are loaded directly from PostgreSQL instead of re-embedding via GPU servers. This enables sweeps on large collections (26k+ chunks) without Segfault crashes. Query embeddings are always computed on-the-fly.

**Pre-flight check:** Before running sweeps, verify the dataset's `collection` name matches the DB (`SELECT DISTINCT collection FROM documents`) and that qrel keys exist in the corpus.

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
| `--rerank` | off | Wrap retriever with RerankerRetriever (cross-encoder reranking) |
| `--rerank-sweep` | off | Run Dense, Dense+Rerank, Sparse, Hybrid, Hybrid+Rerank side-by-side |

**Usage:**
```bash
# Single retriever
./venv/bin/python dev/retrieval/eval/eval_runner.py \
    --dataset searxng_docs --retriever dense --top-k 10

# MRL dimension sweep (dense only, DB-backed)
./venv/bin/python dev/retrieval/eval/eval_runner.py \
    --dataset searxng_docs --mrl-sweep

# Dense vs Sparse vs Hybrid side-by-side
./venv/bin/python dev/retrieval/eval/eval_runner.py \
    --dataset searxng_docs --hybrid-sweep --rrf-k 60

# Dense with reranking
./venv/bin/python dev/retrieval/eval/eval_runner.py \
    --dataset qwen3_paper --retriever dense --rerank

# Full rerank sweep (Dense, Dense+Rerank, Sparse, Hybrid, Hybrid+Rerank)
./venv/bin/python dev/retrieval/eval/eval_runner.py \
    --dataset searxng_docs --rerank-sweep
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

**Purpose:** Dense retriever using Qwen3-Embedding-8B via llama-server (port 8081). Supports optional MRL dimension truncation and DB-backed corpus embeddings.
**Input:** Corpus and query dicts. Optional `truncate_dims` (int) for MRL, optional `query_prefix` (uses Qwen3 instruct format by default), optional `collection` (str) for DB-backed embeddings.
**Output:** BEIR-format results dict `{query_id: {doc_id: cosine_similarity}}`.

When `collection` is set, corpus embeddings are loaded from PostgreSQL (`SELECT embedding FROM documents WHERE collection = X`) instead of re-embedding. MRL truncation + L2 renormalization applied in numpy. Query embeddings always via llama-server.

---

## retrievers/sparse.py

**Purpose:** Sparse retriever using SPLADE++ via splade_server (port 8083). Computes sparse cosine similarity between query and corpus vectors. Supports DB-backed corpus embeddings.
**Input:** Corpus and query dicts. Optional `collection` (str) for DB-backed sparse embeddings.
**Output:** BEIR-format results dict `{query_id: {doc_id: sparse_cosine_score}}`.

When `collection` is set, sparse embeddings are loaded from PostgreSQL (`pgvector.sparsevec.SparseVector` → `indices()` / `values()` methods). Query embeddings always via SPLADE server.

---

## retrievers/reranker.py

**Purpose:** Wrapper that reranks any retriever's results with a cross-encoder (Qwen3-Reranker-0.6B via llama-server port 8082).
**Input:** A base `BaseRetriever` instance, `top_n` candidates to retrieve before reranking (default 50).
**Output:** BEIR-format results dict with cross-encoder relevance scores `{query_id: {doc_id: relevance_score}}`.

Auto-starts reranker server via `server_manager.ensure_ready("reranker")`. Scores are probabilities in [0, 1].

---

## retrievers/hybrid.py

**Purpose:** Hybrid retriever fusing dense and sparse results with Reciprocal Rank Fusion (RRF).
**Input:** `DenseRetriever` and `SparseRetriever` instances, `rrf_k` parameter (default 60).
**Output:** BEIR-format results dict with RRF-fused scores `{query_id: {doc_id: rrf_score}}`.

RRF formula: `score = Σ 1/(k + rank)` summed across both result lists. Documents appearing in both lists are boosted.
