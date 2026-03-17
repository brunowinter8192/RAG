# dev/indexing/ — Indexing Pipeline Evaluation

Scripts for evaluating and profiling the indexing pipeline (chunking, embedding, DB write).

## Documentation Tree

- [llama_server/DOCS.md](llama_server/DOCS.md) — Reranker server debugging scripts

---

## chunking_eval/chunking_sweep.py

**Purpose:** Evaluate chunking strategy variants (chunk size, overlap, separator set) using Document-Level Recall@K. Because chunk IDs change when chunk size changes, ground truth links queries to documents (not individual chunks).
**Input:** Directory of `.md` source files, a document-level dataset JSON, a test DB name, and variant codes.
**Output:** Comparison table (stdout) + JSON results in `chunking_eval/results/sweep_<timestamp>.json`.

**Variants:**

| Code | Chunk Size | Overlap | Separators |
|------|-----------|---------|------------|
| A | 500 | 100 | default |
| B | 750 | 150 | default |
| C | 1000 | 200 | default |
| D | 1500 | 300 | default |
| E | 500 | 100 | markdown |
| F | 750 | 150 | markdown |

**Default separators:** `\n\n`, `\n`, `. `, `! `, `? `, ` `
**Markdown separators:** `# `, `## `, `### `, `\n---\n`, ` ``` `, `\n\n`, `\n`, `. `, ` `

**Dataset format** (`chunking_eval/datasets/*.json`):
```json
{
  "queries": {"q01": "What embedding dimensions does Qwen3 support?"},
  "doc_qrels": {"q01": ["arxiv__2506.05176__qwen3-embedding.md"]}
}
```

**CLI flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--source-dir` | required | Directory with `.md` files to chunk |
| `--dataset` | required | Path to document-level dataset JSON |
| `--db-name` | `rag_test` | PostgreSQL database name (NOT `rag`) |
| `--variants` | `A,B,C,D,E,F` | Comma-separated variant codes |
| `--dry-run` | off | Chunk + show stats only, skip embed/index/eval |

**Setup** (one-time test DB):
```bash
bash dev/indexing/chunking_eval/setup_test_db.sh
./start.sh   # GPU servers required for indexing + eval
```

**Usage:**
```bash
# Full sweep
./venv/bin/python dev/indexing/chunking_eval/chunking_sweep.py \
    --source-dir data/documents/RAG_MCP \
    --dataset dev/indexing/chunking_eval/datasets/rag_mcp_doc_level.json \
    --db-name rag_test

# Specific variants
./venv/bin/python dev/indexing/chunking_eval/chunking_sweep.py \
    --source-dir data/documents/RAG_MCP \
    --dataset dev/indexing/chunking_eval/datasets/rag_mcp_doc_level.json \
    --db-name rag_test --variants A,C,E

# Dry run (chunk stats only)
./venv/bin/python dev/indexing/chunking_eval/chunking_sweep.py \
    --source-dir data/documents/RAG_MCP \
    --dataset dev/indexing/chunking_eval/datasets/rag_mcp_doc_level.json \
    --dry-run
```

---

## embedding_benchmark/benchmark.py

**Purpose:** Measure wall time for sequential vs parallel execution of dense (port 8081) and sparse/SPLADE (port 8083) embedding servers across batch sizes.
**Input:** None (no arguments). Both embedding servers must be running.
**Output:** Comparison table (stdout) with sequential time, parallel time, speedup factor, and output identity check for batch sizes 8, 16, 32, 64.

**Expected speedup:** ~1.5–2x (dense + SPLADE run concurrently via `ThreadPoolExecutor(max_workers=2)`).

**Usage:**
```bash
./venv/bin/python dev/indexing/embedding_benchmark/benchmark.py
```

---

## indexing_benchmark/benchmark.py

**Purpose:** Profile the full indexing pipeline (dense embed + sparse embed + DB write) per batch, with per-component timing.
**Input:** Path to a `chunks.json` file. Optional `--batch-size`, `--max-batches`, `--skip-db` flags.
**Output:** Per-batch timing table (dense, sparse, wall, DB columns) + summary with throughput (chunks/s).

**CLI flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | required | Path to `chunks.json` |
| `--batch-size` | 32 | Chunks per batch |
| `--max-batches` | 0 (all) | Limit number of batches |
| `--skip-db` | off | Skip DB insert timing (embed only) |

**Usage:**
```bash
./venv/bin/python dev/indexing/indexing_benchmark/benchmark.py \
    --input data/documents/RAG_MCP/chunks.json

./venv/bin/python dev/indexing/indexing_benchmark/benchmark.py \
    --input data/documents/RAG_MCP/chunks.json \
    --batch-size 16 --max-batches 5 --skip-db
```

---

## splade_truncation/reproduce.py

**Problem:** SPLADE server produces corrupted sparse vectors (14k-30k non-zero elements instead of 100-200) after prolonged uptime. pgvector sparsevec type crashes at >16,000 non-zero elements. Root cause not isolated — correlation with server uptime observed but not causally proven.

**Purpose:** Analyze SPLADE non-zero element distribution across document chunks and test pgvector INSERT behavior.
**Input:** One or more pre-chunked JSON files (from `data/documents/`). SPLADE server must be running (port 8083).
**Output:** Distribution stats (min, max, mean, median, p95, p99), histogram, list of chunks exceeding 16,000 nnz. Optionally attempts INSERT into `rag_test` DB.

**Status:** Reproduction script only. Missing: `test_truncation.py` (test top-K truncation impact), monitoring script (track nnz over server uptime).

**Usage:**
```bash
# Analyze element distribution (no DB needed)
./venv/bin/python dev/indexing/splade_truncation/reproduce.py --analyze-only \
    --input data/documents/searxng/Meta_Search_Engine_Optimization.json

# Full test with DB insert (requires rag_test DB)
POSTGRES_DB=rag_test ./venv/bin/python dev/indexing/splade_truncation/reproduce.py \
    --input data/documents/searxng/Meta_Search_Engine_Optimization.json
```
