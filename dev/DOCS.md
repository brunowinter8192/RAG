# dev/ — Development & Evaluation Scripts

Pipeline-oriented layout matching the RAG system architecture. Exempt from CLAUDE.md compliance.

## Structure

### Indexing Pipeline (`indexing/`)

| Directory | Purpose | Key Scripts |
|-----------|---------|-------------|
| `chunking_eval/` | Chunking strategy evaluation (chunk size, separators) | TBD |
| `embedding_benchmark/` | Dense+SPLADE parallel embedding benchmark | `benchmark.py` |
| `indexing_benchmark/` | DB write profiling (batch timing) | `benchmark.py` |
| `llama_server/` | llama-server debugging (500 errors, batch size) | `01_capture_stderr.py`, `02_reproduce_500.py`, `03_test_batch_size.py` |

### Retrieval Pipeline (`retrieval/`)

| Directory | Purpose | Key Scripts |
|-----------|---------|-------------|
| `eval/` | BEIR-format retrieval evaluation (pytrec_eval) | `eval_runner.py` |
| `reranker_8b/` | Reranker 8B GGUF validation | `test_8b_reranker.py` |

### Data Preparation (`cleanup/`)

| Directory | Purpose | Key Scripts |
|-----------|---------|-------------|
| `cleanup/` | Web markdown cleanup scripts (per-collection) | `clean_web_SearXNG_Docs.py`, `clean_web_RAG_MCP.py` |

## Usage

All scripts run from project root with the project venv:

```bash
./venv/bin/python dev/<path>/<script>.py [args]
```

Scripts that access the database import from `src.rag` and expect PostgreSQL on port 5433.

## retrieval/eval/

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
./venv/bin/python dev/retrieval/eval/eval_runner.py --dataset searxng_docs --retriever dense --top-k 10

# MRL dimension sweep (dense only)
./venv/bin/python dev/retrieval/eval/eval_runner.py --dataset qwen3_paper --mrl-sweep

# Dense vs Sparse vs Hybrid side-by-side
./venv/bin/python dev/retrieval/eval/eval_runner.py --dataset searxng_docs --hybrid-sweep --rrf-k 60
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

**Dataset format** (`dev/retrieval/eval/datasets/*.json`):

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

Results are saved to `dev/retrieval/eval/results/<dataset>_<retriever>.json`.
