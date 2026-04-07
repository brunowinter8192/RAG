# dev/indexing/ — Indexing Pipeline Evaluation

Scripts for evaluating and profiling the indexing pipeline (chunking, embedding, DB write).

## Documentation Tree

- [llama_server/DOCS.md](llama_server/DOCS.md) — Reranker server debugging scripts

---

## Self-Contained Dev Suite (no src/rag imports)

Standalone modules and scripts for indexing and retrieval experiments. All modules live in `dev/indexing/` and are imported via `sys.path.insert(0, Path(__file__).parent)`. DB: `rag_test` (never `rag`). Vector dim: 1024 (MRL-truncated from 4096).

**Note:** If `rag_test` already has a `documents` table with `vector(4096)` (created by chunking_eval), drop it before using this suite:
```bash
docker exec rag-postgres psql -U rag -d rag_test -c "DROP TABLE IF EXISTS documents;"
```

### Module Files

| File | Purpose |
|------|---------|
| `chunker.py` | Recursive char split — `chunk_file(path)`, `chunk_text(text, size, overlap)` |
| `embedder.py` | Dense embedding client — `embed(texts, prefix)`, `truncate_mrl(embeddings, dims=1024)` |
| `sparse_embedder.py` | SPLADE client — `embed_sparse(texts)` |
| `db.py` | DB operations — `get_connection()`, `ensure_schema()`, `store_chunks()`, `search_dense/sparse/hybrid()` |
| `indexer.py` | Orchestrator — `index_file(path, collection, conn)`, `index_directory(dir, collection, conn)` |
| `retriever.py` | Retrieval — `retrieve_dense/sparse/hybrid(query, collection, top_k)`, `rerank(query, results, top_k)` |

### Config Defaults

| Parameter | Value |
|-----------|-------|
| CHUNK_SIZE | 2000 chars |
| OVERLAP | 400 chars |
| MRL dims | 1024 (from 4096) |
| Batch size | 32 |
| DB | rag_test, port 5433, user rag |

---

## 02_index_collection.py

**Purpose:** Index a directory of `.md` files into `rag_test` DB with configurable chunking.

**Prerequisites:** Embedding server (port 8081) + SPLADE server (port 8083) must be running.

**CLI flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--source-dir` | required | Directory with `.md` files |
| `--collection` | source-dir basename | Collection name in DB |
| `--chunk-size` | 2000 | Chunk size in chars |
| `--overlap` | 400 | Overlap in chars |

**Output:** `02_reports/index_<collection>_<timestamp>.md` — config, per-doc stats, totals, errors.

**Usage:**
```bash
./venv/bin/python dev/indexing/02_index_collection.py \
    --source-dir data/documents/RAG_MCP \
    --collection RAG_MCP

./venv/bin/python dev/indexing/02_index_collection.py \
    --source-dir data/documents/RAG_MCP \
    --collection RAG_MCP_500 \
    --chunk-size 500 --overlap 100
```

---

## 03_retrieval_sandbox.py

**Purpose:** Test retrieval quality across dense/sparse/hybrid/rerank modes for a set of queries.

**Prerequisites:** Embedding (8081) + SPLADE (8083) for all modes. Reranker (8082) for `hybrid+rerank`.

**Queries JSON format:**
```json
["What embedding dimensions does Qwen3 support?", "How does SPLADE work?"]
```

**CLI flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--collection` | required | Collection name to query |
| `--queries` | required | Path to JSON file with query list |
| `--top-k` | 5 | Results per query per mode |
| `--modes` | `dense,sparse,hybrid,hybrid+rerank` | Comma-separated modes |

**Output:** `03_reports/retrieval_<collection>_<timestamp>.md` — per query, per mode: rank/score/doc/snippet table.

**Usage:**
```bash
./venv/bin/python dev/indexing/03_retrieval_sandbox.py \
    --collection RAG_MCP \
    --queries dev/indexing/chunking_eval/datasets/rag_mcp_doc_level.json \
    --top-k 5 \
    --modes dense,sparse,hybrid

./venv/bin/python dev/indexing/03_retrieval_sandbox.py \
    --collection RAG_MCP \
    --queries dev/indexing/chunking_eval/datasets/rag_mcp_doc_level.json \
    --modes hybrid+rerank
```

---

## chunking_eval/01_chunking_sweep.py

**Purpose:** Evaluate chunking strategy variants (chunk size, overlap, separator set) using Document-Level Recall@K. Because chunk IDs change when chunk size changes, ground truth links queries to documents (not individual chunks).
**Input:** Directory of `.md` source files, a document-level dataset JSON, a test DB name, and variant codes.
**Output:** Comparison table (stdout) + JSON results in `chunking_eval/01_reports/sweep_<timestamp>.json`.

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

**Datasets** (`chunking_eval/datasets/`):
- `rag_mcp_doc_level.json` — Full dataset: 18 queries, 20/23 docs covered
- `rag_mcp_subset.json` — 5-doc subset: 7 queries (q01, q02, q06, q07, q08, q10, q15)

**Corpus subset** (`chunking_eval/corpus/`): Symlinks to 5 representative RAG_MCP docs for faster sweeps. Created 2026-03-18.

**Sweep result (2026-03-18):** 5-doc subset, all 6 variants → Recall@3/5/10 = 1.000. **Not discriminating** — corpus too small. Needs larger benchmark dataset (MS-MARCO subset or full RAG_MCP with more queries).

**Setup** (one-time test DB):
```bash
bash dev/indexing/chunking_eval/setup_test_db.sh  # or: docker exec rag-postgres psql -U rag -d postgres -c "CREATE DATABASE rag_test;"
./start.sh   # GPU servers required for indexing + eval
```

**Usage:**
```bash
# Full sweep
./venv/bin/python dev/indexing/chunking_eval/01_chunking_sweep.py \
    --source-dir data/documents/RAG_MCP \
    --dataset dev/indexing/chunking_eval/datasets/rag_mcp_doc_level.json \
    --db-name rag_test

# Subset sweep (faster, 5 docs)
./venv/bin/python dev/indexing/chunking_eval/01_chunking_sweep.py \
    --source-dir dev/indexing/chunking_eval/corpus \
    --dataset dev/indexing/chunking_eval/datasets/rag_mcp_subset.json \
    --db-name rag_test

# Dry run (chunk stats only)
./venv/bin/python dev/indexing/chunking_eval/01_chunking_sweep.py \
    --source-dir data/documents/RAG_MCP \
    --dataset dev/indexing/chunking_eval/datasets/rag_mcp_doc_level.json \
    --dry-run
```

---

## embedding_benchmark/01_benchmark.py

**Purpose:** Measure wall time for sequential vs parallel execution of dense (port 8081) and sparse/SPLADE (port 8083) embedding servers across batch sizes.
**Input:** None (no arguments). Both embedding servers must be running.
**Output:** Comparison table (stdout) with sequential time, parallel time, speedup factor, and output identity check for batch sizes 8, 16, 32, 64.

**Expected speedup:** ~1.5–2x (dense + SPLADE run concurrently via `ThreadPoolExecutor(max_workers=2)`).

**Usage:**
```bash
./venv/bin/python dev/indexing/embedding_benchmark/01_benchmark.py
```

---

## indexing_benchmark/01_benchmark.py

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
./venv/bin/python dev/indexing/indexing_benchmark/01_benchmark.py \
    --input data/documents/RAG_MCP/chunks.json

./venv/bin/python dev/indexing/indexing_benchmark/01_benchmark.py \
    --input data/documents/RAG_MCP/chunks.json \
    --batch-size 16 --max-batches 5 --skip-db
```

---

## splade_truncation/

### Problem

SPLADE server (`src/rag/splade_server.py`) produces corrupted sparse vectors after prolonged uptime (8h+): 14,000-30,000 non-zero elements instead of the expected 100-200. pgvector sparsevec type has a hard limit of 16,000 nnz — exceeding it crashes indexing with `ProgramLimitExceeded`. Restarting the server immediately fixes it. Root cause not isolated.

Production code status quo and safety-net details → `decisions/index03_sparse_embedding.md`

### Investigation

#### Code Analysis

- **SparseEncoder.encode()** (`venv/.../SparseEncoder.py:499,595`): Calls `self.eval()` and wraps forward pass in `torch.inference_mode()` — correct, no gradient accumulation possible.
- **SpladePooling.forward()** (`venv/.../SpladePooling.py:62-133`): In-place ops (`relu_()`, `log1p_()`) operate on new tensors per call, not on model weights. No state accumulation.
- **MLMTransformer.forward()** (`venv/.../MLMTransformer.py:196-210`): Passes features through `AutoModelForMaskedLM`, extracts logits. Stateless.
- **Device = MPS (Metal)** via auto-detection (`venv/.../util/environment.py:32`). On Apple Silicon, `torch.backends.mps.is_available()` returns True → SPLADE runs on Metal GPU.
- **Our implementation is standard-conforming.** `model.encode(texts, convert_to_tensor=False)` is the correct API usage.

#### External Research (2026-03-18)

| Source | Result | Relevance |
|--------|--------|-----------|
| sentence-transformers #3431 | nnz explosion during **training** (all 31k dims active) | Medium — same effect, different trigger (training vs inference) |
| sentence-transformers #3545 | Eval score degradation from corpus handling bug | Low — different symptom |
| sentence-transformers #1795 | Memory growth in `encode()` during first ~10k predictions, then stabilizes | Medium — different pattern (stabilizes, ours explodes) |
| sentence-transformers v3.4.0 | Memory leak fix (circular dependency Trainer→Model) | Low — unclear if SparseEncoder affected |
| Web search (11 queries, 292 results) | 0 matches for nnz explosion in long-running SPLADE servers | — |
| Reddit (5 subreddits: ML, pytorch, LocalLLaMA, NLP, learnML) | 0 direct matches. PyTorch M1 memory leak (2022, fixed). | Low |
| GitHub code search (5 reference implementations) | All use global model + encode() — same pattern as ours. None mention long-running degradation. | Confirms our implementation is standard |

**Conclusion:** No publicly documented case of this problem. SPLADE in long-running production servers is extremely niche.

#### Hypotheses

| Hypothesis | Status | Evidence |
|------------|--------|----------|
| MPS (Metal) numerical drift over time | **Active — unverified** | Device confirmed as MPS. MPS has known precision issues in PyTorch. Strongest candidate. |
| PyTorch internal buffer growth | Unverified | Would explain time-correlation. No direct evidence. |
| Memory pressure → precision loss | Unverified | Plausible but no measurement data yet. |
| sentence-transformers internal caching | **Excluded** | Code analysis shows no stateful caching in encode/forward chain. |
| Missing eval()/no_grad() | **Excluded** | Library calls both internally (Z.499, Z.595). |
| Gradient accumulation | **Excluded** | `torch.inference_mode()` prevents this. |

### Scripts

- **reproduce.py** — Analyze SPLADE nnz distribution across document chunks + pgvector INSERT test.
- **monitor.py** — Periodically probe running SPLADE server, track nnz/RSS/memory over time to CSV.

```bash
# Reproduce: analyze element distribution
./venv/bin/python dev/indexing/splade_truncation/reproduce.py --analyze-only \
    --input data/documents/searxng/Meta_Search_Engine_Optimization.json

# Monitor: single baseline probe
./venv/bin/python dev/indexing/splade_truncation/monitor.py --once

# Monitor: continuous (every 2min, CSV output)
./venv/bin/python dev/indexing/splade_truncation/monitor.py --interval 120
```
