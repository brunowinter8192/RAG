# dev/ — Development & Debugging Scripts

Standalone scripts for testing, debugging, and data preparation. Exempt from CLAUDE.md compliance.

## Directories

| Directory | Purpose | Key Scripts |
|-----------|---------|-------------|
| `cleanup/` | SearXNG Sphinx docs cleaning (v2, production) | `clean_web_SearXNG_Docs.py` |
| `explore/` | Pattern analysis & initial cleaning (v1, predecessor to cleanup/) | `analyze_patterns.py`, `clean_searxng.py` |
| `llama_server/` | llama-server debugging (reranker 500 errors, batch size tuning) | `01_capture_stderr.py`, `02_reproduce_500.py`, `03_test_batch_size.py` |
| `splade_benchmark/` | Sequential vs parallel embedding benchmark (dense + SPLADE) | `benchmark.py` |
| `reranker_8b/` | Reranker 8B GGUF validation (mradermacher defect detection) | `test_8b_reranker.py` |
| `indexing_benchmark/` | Indexing pipeline profiling (dense, sparse, DB timing per batch) | `benchmark.py` |
| `retrieval_eval/` | Retrieval quality evaluation (BEIR-format, pytrec_eval metrics) | `eval_runner.py` |

## Usage

All scripts run from project root with the project venv:

```bash
./venv/bin/python dev/<directory>/<script>.py [args]
```

Scripts that access the database import from `src.rag` and expect PostgreSQL on port 5433.

## retrieval_eval/

BEIR-format evaluation suite measuring retrieval quality with `pytrec_eval` metrics.

**Metrics:** NDCG, Recall, Precision — evaluated at k=3, 5, 10

**Retriever types:**

| Retriever | Class | Description |
|-----------|-------|-------------|
| `dense` | `DenseRetriever` | Qwen3-Embedding-8B via llama-server (port 8081), optional MRL truncation |
| `sparse` | `SparseRetriever` | SPLADE via splade_server (port 8083) |
| `hybrid` | `HybridRetriever` | RRF fusion of dense + sparse |

**CLI Usage:**

```bash
# Single retriever
./venv/bin/python dev/retrieval_eval/eval_runner.py --dataset searxng_docs --retriever dense --top-k 10

# MRL dimension sweep (dense only)
./venv/bin/python dev/retrieval_eval/eval_runner.py --dataset qwen3_paper --mrl-sweep

# Dense vs Sparse vs Hybrid side-by-side
./venv/bin/python dev/retrieval_eval/eval_runner.py --dataset searxng_docs --hybrid-sweep --rrf-k 60
```

**CLI flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--dataset` | required | Dataset name (without .json), from `datasets/` |
| `--retriever` | dense | `dense`, `sparse`, or `hybrid` |
| `--top-k` | 10 | Number of results to retrieve |
| `--truncate-dims` | None | MRL dimension truncation (dense only) |
| `--rrf-k` | 60 | RRF k parameter for hybrid fusion |
| `--mrl-sweep` | off | Run dense across dims 256, 512, 1024, 2048, full |
| `--hybrid-sweep` | off | Run dense + sparse + hybrid side-by-side |

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

If `corpus` is absent and `corpus_from_db: true`, corpus is loaded from PostgreSQL for the named collection. If `source_json` is set, corpus is built from the chunks.json file.

Results are saved to `results/<dataset>_<retriever>.json`.
