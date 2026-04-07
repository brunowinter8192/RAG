# dev/indexing/ — Indexing Pipeline Dev Suite

Self-contained modules and scripts for indexing experiments. No imports from `src/rag/`. DB: `rag_test` (never `rag`). Vector dim: 1024 (MRL-truncated from 4096d).

All scripts run from project root:
```bash
./venv/bin/python dev/indexing/<script>.py [args]
```

**Note:** If `rag_test` already has a `documents` table with `vector(4096)` from other dev suites, drop it first:
```bash
docker exec rag-postgres psql -U rag -d rag_test -c "DROP TABLE IF EXISTS documents;"
```

---

## Pipeline Modules

Modules are prefixed `pN_` to indicate pipe position. Import via `sys.path.insert(0, "dev/indexing/")`.

| File | Pipe Position | Purpose |
|------|--------------|---------|
| `p1_chunker.py` | 1 — Chunking | `chunk_file(path)`, `chunk_text(text, size, overlap)` |
| `p2_embedder.py` | 2 — Dense Embed | `embed(texts, prefix)`, `truncate_mrl(embeddings, dims=1024)` |
| `p3_sparse_embedder.py` | 3 — Sparse Embed | `embed_sparse(texts)` |
| `p4_db.py` | 4 — Storage | `get_connection()`, `ensure_schema()`, `store_chunks()`, `search_dense/sparse/hybrid()` |
| `p5_indexer.py` | 5 — Orchestrator | `index_file(path, collection, conn)`, `index_directory(dir, collection, conn)` |

### Config Defaults

| Parameter | Value |
|-----------|-------|
| CHUNK_SIZE | 2000 chars |
| OVERLAP | 400 chars |
| MRL dims | 1024 (truncated from 4096) |
| Batch size | 32 |
| DB | rag_test, port 5433, user rag |

---

## A_chunking_stats.py

**Purpose:** Analyze chunking output for a directory. No GPU, no DB, no embedding — instant.

**CLI flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--source-dir` | required | Directory with `.md` files |
| `--chunk-size` | 2000 | Chunk size in chars |
| `--overlap` | 400 | Overlap in chars |

**Output:** `A_chunking_stats_reports/stats_<collection>_<timestamp>.md` — per-doc table (file size, chunks, avg/min/max chunk size) + summary + size distribution buckets.

**Usage:**
```bash
./venv/bin/python dev/indexing/A_chunking_stats.py \
    --source-dir data/documents/RAG_MCP

./venv/bin/python dev/indexing/A_chunking_stats.py \
    --source-dir data/documents/RAG_MCP \
    --chunk-size 1000 --overlap 200
```

---

## A_index_collection.py

**Purpose:** Index a directory of `.md` files into `rag_test` DB.

**Prerequisites:** Embedding server (port 8081) + SPLADE server (port 8083) running.

**CLI flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--source-dir` | required | Directory with `.md` files |
| `--collection` | source-dir basename | Collection name in DB |
| `--chunk-size` | 2000 | Chunk size in chars |
| `--overlap` | 400 | Overlap in chars |

**Output:** `A_index_collection_reports/index_<collection>_<timestamp>.md` — config, per-doc stats, totals, throughput, errors.

**Usage:**
```bash
./venv/bin/python dev/indexing/A_index_collection.py \
    --source-dir data/documents/RAG_MCP \
    --collection RAG_MCP

./venv/bin/python dev/indexing/A_index_collection.py \
    --source-dir data/documents/RAG_MCP \
    --collection RAG_MCP_small \
    --chunk-size 500 --overlap 100
```
