# src/rag/ — RAG Pipeline Modules

## Role

Core implementation of the hybrid RAG pipeline: dense (Qwen3) + sparse (SPLADE) embedding, PostgreSQL/pgvector storage, retrieval with CC/RRF fusion and cross-encoder reranking, and GPU server lifecycle management. Touch this package when changing retrieval logic, embedding models, search algorithms, indexing behavior, or server startup. Do NOT touch for Skills/Commands (project root) or dev scripts (`dev/`).

## Public Interface

`__init__.py` is empty — import directly from sub-modules:
- `from src.rag.retriever import search_workflow, format_results` — primary entry point (cli.py, workflow.py)
- `from src.rag.db import get_connection` — direct DB access in scripts

## Flow

**Retrieval (per query):** `retriever.py` workflow → `db.py` opens connection + validates collection → `search_primitives.py` embeds query and runs vector / BM25 / SPLADE search → `fusion.py` fuses results → `reranker.py` re-scores → `formatting.py` serializes output. Context expansion (neighboring chunks) is done on demand via `read_document_workflow` using `--before`/`--after`.

**Indexing (per batch):** `chunker.py` splits document → `indexer.py` embeds chunks via `embedder.py` + `sparse_embedder.py` and inserts into PostgreSQL. `server_manager.py` ensures GPU servers are running before embedding starts.

## Modules

### db.py (93 LOC)

**Purpose:** PostgreSQL connection factory, collection/document queries, and WHERE-clause filter builder shared across retrieval sub-modules.
**Reads:** `.env` (POSTGRES_* connection params); PostgreSQL `documents` table.
**Writes:** nothing (read-only queries).
**Called by:** retriever.py, search_primitives.py
**Calls out:** psycopg2, pgvector, python-dotenv

---

### embedder.py (62 LOC)

**Purpose:** HTTP client for the llama-server dense embedding endpoint; auto-starts the embedding GPU server on first call via `server_manager.ensure_ready`.
**Reads:** `EMBEDDING_URL`, `EMBEDDING_MODEL` from env; llama-server `/v1/embeddings` response.
**Writes:** nothing.
**Called by:** search_primitives.py, indexer.py
**Calls out:** requests

---

### sparse_embedder.py (47 LOC)

**Purpose:** HTTP client for the SPLADE server sparse embedding endpoint; mirrors `embedder.py` interface.
**Reads:** `SPLADE_URL` from env; SPLADE server `/v1/sparse-embeddings` response.
**Writes:** nothing.
**Called by:** search_primitives.py, indexer.py
**Calls out:** requests

---

### reranker.py (55 LOC)

**Purpose:** HTTP client for the llama-server cross-encoder reranking endpoint; re-scores candidate result lists by query-document relevance.
**Reads:** `RERANKER_URL` from env; llama-server `/v1/rerank` response.
**Writes:** nothing.
**Called by:** retriever.py
**Calls out:** requests

---

### search_primitives.py (173 LOC)

**Purpose:** Low-level search functions — `embed_query`, vector cosine search, BM25 full-text search, and SPLADE sparse search against PostgreSQL.
**Reads:** PostgreSQL `documents` table (via `conn` parameter); embedding and SPLADE servers (via embedder/sparse_embedder).
**Writes:** nothing.
**Called by:** retriever.py
**Calls out:** (none — all via internal modules: db, embedder, sparse_embedder)

---

### fusion.py (52 LOC)

**Purpose:** Fuse two ranked result lists via Reciprocal Rank Fusion (`rrf_fusion`) or Convex Combination with min-max normalization (`cc_fusion`). Pure Python, no I/O.
**Reads:** in-memory result lists.
**Writes:** nothing.
**Called by:** retriever.py
**Calls out:** (none — pure Python)

---

### formatting.py (38 LOC)

**Purpose:** Serialize search results, collections, and document lists as human-readable strings for CLI stdout.
**Reads:** in-memory result lists.
**Writes:** nothing.
**Called by:** retriever.py (imported then re-exported — see Gotchas)
**Calls out:** (none — pure Python)

---

### retriever.py (145 LOC)

**Purpose:** Workflow orchestration for all six retrieval operations (search, search_hybrid, search_keyword, list_collections, list_documents, read_document). Thin shell composing db, search_primitives, fusion, formatting, and reranker sub-modules. Hosts `merge_chunks` + `find_overlap` helpers (chunk context expansion for read_document). Re-exports `format_*` functions for cli.py backward compatibility.
**Reads:** PostgreSQL via db; embedding/SPLADE/reranker servers via search_primitives/reranker.
**Writes:** `src/rag/logs/retriever.log` (via `logging.basicConfig`).
**Called by:** cli.py, workflow.py
**Calls out:** (none — all external calls delegated to sub-modules)

---

### chunker.py (116 LOC)

**Purpose:** Split markdown documents into semantic chunks using recursive character splitting at paragraph → sentence → word boundaries.
**Reads:** markdown file from disk.
**Writes:** nothing (returns chunk list; caller writes JSON).
**Called by:** workflow.py
**Calls out:** (none — pure Python)

---

### indexer.py (268 LOC)

**Purpose:** Index chunks into PostgreSQL with dense + sparse embeddings; handles schema creation, batch insert, SPLADE backfill, and deletion by collection/document.
**Reads:** `chunks.json` from disk; `.env` for connection params; PostgreSQL schema state.
**Writes:** PostgreSQL `documents` table (insert, delete, schema init).
**Called by:** workflow.py
**Calls out:** psycopg2, pgvector, python-dotenv

---

### server_manager.py (351 LOC)

**Purpose:** Centralized lifecycle manager for all three GPU servers — embedding (port 8081), reranker (8082), SPLADE (8083). Handles start, stop, restart, health check, and idle-timeout auto-stop.
**Reads:** server health endpoints; `/tmp/rag-server-{name}-last-used` timestamp files; process port occupancy.
**Writes:** `/tmp/rag-server-{name}-last-used` idle timestamps; spawns/kills server processes.
**Called by:** embedder.py, sparse_embedder.py, reranker.py, workflow.py (lazy import for `index-dir` and `server` subcommands)
**Calls out:** requests, subprocess

**Refactor candidate (351 LOC > 300-LOC threshold)** — no concrete pain-points today, tracked as known debt.

---

### splade_server.py (67 LOC)

**Purpose:** Standalone FastAPI server that loads the SPLADE model at startup and exposes `/v1/sparse-embeddings` and `/health` on port 8083.
**Reads:** HuggingFace model (`naver/splade-cocondenser-ensembledistil`) from disk/HF cache at startup.
**Writes:** nothing.
**Called by:** (none — subprocess target launched by `server_manager.py`, never imported by Python code)
**Calls out:** fastapi, uvicorn, torch, transformers

---

## State

| Owner | State | Reads | Writes |
|---|---|---|---|
| PostgreSQL `documents` table | All indexed chunks with dense + sparse embeddings | db.py, search_primitives.py | indexer.py (insert/delete/schema) |
| `/tmp/rag-server-{name}-last-used` | Last-used timestamps for idle-timeout | server_manager.py (idle checker) | server_manager.py (ensure_ready) |

## Gotchas

- **splade_server.py has no Python import callers** — appears as dead code in any import grep but is the subprocess target launched by `server_manager.py`. Do not delete.
- **retriever.py re-exports format_results / format_collections / format_documents** from `formatting.py`. `cli.py` imports these from `src.rag.retriever`, not `src.rag.formatting`. Keep the import in retriever.py's INFRASTRUCTURE or cli.py breaks.
- **DEFAULT_QUERY_PREFIX** lives in `search_primitives.py`, not retriever.py — it moved with `embed_query()` during the retriever split refactor.
- **server_manager.py 351 LOC** — exceeds the 300-LOC refactor threshold. No concrete pain-points today; tracked as known debt.
