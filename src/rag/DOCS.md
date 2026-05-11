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

**Manifest-driven sync (per project, end of session):** `sync.py` reads `<project>/.rag-docs.json`, expands the include-globs, hashes each matched `.md` file, and diffs against the `indexed_files` tracking table. Only added/updated files are re-chunked + re-embedded; removed files are deleted from the index; unchanged files are skipped. Reuses chunker/indexer/server_manager primitives — no re-implementation of embedding or storage.

## Modules

### db.py (142 LOC)

**Purpose:** PostgreSQL connection factory, collection/document queries, and WHERE-clause filter builder shared across retrieval sub-modules.
**Reads:** `.env` (POSTGRES_* connection params); PostgreSQL `documents` table.
**Writes:** nothing (read-only queries).
**Called by:** retriever.py, search_primitives.py, indexer.py, sync.py, status.py, workflow.py
**Calls out:** psycopg2, pgvector, python-dotenv

---

### embedder.py (74 LOC)

**Purpose:** HTTP client for the llama-server dense embedding endpoint; auto-starts the embedding GPU server on first call via `server_manager.ensure_ready`.
**Reads:** `EMBEDDING_URL` env (override) or `server_manager.find_server_url('embedding')` for URL; llama-server `/v1/embeddings` response.
**Writes:** `src/rag/logs/embedder.log`.
**Called by:** search_primitives.py, indexer.py
**Calls out:** httpx

---

### sparse_embedder.py (58 LOC)

**Purpose:** HTTP client for the SPLADE server sparse embedding endpoint; mirrors `embedder.py` interface.
**Reads:** `SPLADE_URL` env (override) or `server_manager.find_server_url('splade')` for URL; SPLADE server `/v1/sparse-embeddings` response.
**Writes:** `src/rag/logs/sparse_embedder.log`.
**Called by:** search_primitives.py, indexer.py
**Calls out:** httpx

---

### reranker.py (66 LOC)

**Purpose:** HTTP client for the llama-server cross-encoder reranking endpoint; re-scores candidate result lists by query-document relevance.
**Reads:** `RERANKER_URL` env (override) or `server_manager.find_server_url('reranker')` for URL; llama-server `/v1/rerank` response.
**Writes:** `src/rag/logs/reranker.log`.
**Called by:** retriever.py
**Calls out:** httpx

---

### search_primitives.py (173 LOC)

**Purpose:** Low-level search functions — `embed_query`, vector cosine search, BM25 full-text search, and SPLADE sparse search against PostgreSQL.
**Reads:** PostgreSQL `documents` table (via `conn` parameter); embedding and SPLADE servers (via embedder/sparse_embedder).
**Writes:** nothing.
**Called by:** retriever.py
**Calls out:** (none — all via internal modules: db, embedder, sparse_embedder)

---

### fusion.py (54 LOC)

**Purpose:** Fuse two ranked result lists via Reciprocal Rank Fusion (`rrf_fusion`) or Convex Combination with min-max normalization (`cc_fusion`). Pure Python, no I/O.
**Reads:** in-memory result lists.
**Writes:** nothing.
**Called by:** retriever.py
**Calls out:** (none — pure Python)

---

### formatting.py (59 LOC)

**Purpose:** Serialize search results, collections, and document lists as human-readable strings for CLI stdout.
**Reads:** in-memory result lists.
**Writes:** nothing.
**Called by:** retriever.py (imported then re-exported — see Gotchas)
**Calls out:** (none — pure Python)

---

### retriever.py (151 LOC)

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
**Called by:** workflow.py, sync.py
**Calls out:** (none — pure Python)

---

### indexer.py (301 LOC)

**Purpose:** Index chunks into PostgreSQL with dense + sparse embeddings; handles schema creation, batch insert, SPLADE backfill, deletion by collection/document, and per-document completeness check (`doc_is_complete`) used by workflow.py for adopt-on-complete skip logic.
**Reads:** `chunks.json` from disk; `.env` for connection params; PostgreSQL schema state.
**Writes:** PostgreSQL `documents` table (insert, delete, schema init).
**Called by:** workflow.py, sync.py, cli.py (lazy import for `delete` subcommand)
**Calls out:** psycopg2, pgvector, python-dotenv

---

### sync.py (324 LOC)

**Purpose:** Manifest-driven project doc indexing with hash-based change detection. Reads `<project>/.rag-docs.json` (single- or multi-collection format — `"collection"` key for legacy, `"collections"` array for multi), expands include-globs, hashes matched `.md` files, diffs against the `indexed_files` table, and only re-indexes the deltas. Multi-collection result is keyed by collection name; single-collection is the flat dict (backward-compatible). Composes existing chunker / indexer / server_manager primitives — no re-implementation of embedding or storage.
**Reads:** `<project>/.rag-docs.json` manifest; matched `.md` files from disk; PostgreSQL `indexed_files` table.
**Writes:** `src/rag/logs/sync.log`; PostgreSQL `indexed_files` (upsert/delete) and `documents` (via indexer primitives).
**Called by:** cli.py (`update_docs` subcommand), workflow.py
**Calls out:** hashlib, json, pathlib, logging (stdlib only — all RAG-specific calls are intra-package: chunker, indexer, db, server_manager)

---

### server_manager.py (1061 LOC)

**Purpose:** Centralized lifecycle manager for all five GPU server presets (embedding-8b, embedding-0.6b, reranker-0.6b, reranker-8b, splade) plus arbitrary llama-server instances. Handles start, stop, restart, health check, idle-timeout auto-stop, orphan purge, and `rag-cli server` CLI surface. Port discovery via `_resolve_port` (tries default port; falls back to kernel-allocated ephemeral). Watchdog runs as **detached subprocess** (via `_ensure_watchdog_process`) — survives the spawning CLI process exit through `start_new_session=True`. Single-instance enforced via PID lock file `~/.rag-locks/watchdog.pid`.
**Reads:** server health endpoints (`/health`); `~/.rag-locks/server-port-{N}.json` state files (pid, port, model, log_path); `~/.rag-locks/watchdog.pid`; log file mtimes (for idle computation).
**Writes:** `~/.rag-locks/server-port-{N}.json` (written after Popen, unlinked on stop); `~/.rag-locks/watchdog.pid`; spawns/kills server processes; spawns watchdog subprocess; delegates structured errors to `error_log`.
**Called by:** embedder.py, sparse_embedder.py, reranker.py, workflow.py (lazy import for `index-dir` and `server` subcommands), cli.py (lazy import for `server` subcommand), sync.py (`ensure_ready` before embed), indexer.py (lazy import of `RAG_ROOT`), status.py, watchdog_main.py (`_watchdog_loop`).
**Calls out:** httpx, subprocess.

---

### watchdog_main.py (7 LOC)

**Purpose:** Standalone watchdog entrypoint — invoked as `python -m src.rag.watchdog_main`. Imports server_manager and runs `_watchdog_loop()` directly. Spawned as detached process by `_ensure_watchdog_process()`; survives parent exit.
**Reads:** indirect (via `_watchdog_loop`).
**Writes:** indirect (via `stop`).
**Called by:** subprocess invocation only — no Python imports.
**Calls out:** server_manager (intra-package).

---

### splade_server.py (67 LOC)

**Purpose:** Standalone FastAPI server that loads the SPLADE model at startup and exposes `/v1/sparse-embeddings` and `/health` on port 8083.
**Reads:** HuggingFace model (`naver/splade-v3`, `MAX_ACTIVE_DIMS = 256`) from disk/HF cache at startup.
**Writes:** nothing.
**Called by:** (none — subprocess target launched by `server_manager.py`, never imported by Python code)
**Calls out:** fastapi, uvicorn, torch, transformers

---

### lock.py (132 LOC)

**Purpose:** Global RAG mutex via `fcntl.flock` + JSON lockfile; provides `acquire` context manager, `read`, `update_progress`, and `heartbeat` functions used by workflow and CLI.
**Reads:** `~/.rag-locks/rag.flock` (fd hold); `~/.rag-locks/rag.lock` (JSON details).
**Writes:** `~/.rag-locks/rag.flock`; `~/.rag-locks/rag.lock` (atomic tmp+rename with pid, command, started_at, heartbeat, progress).
**Called by:** cli.py, workflow.py, status.py (read-only via `read`)
**Calls out:** (none — stdlib only: fcntl, json, os, pathlib)

---

### status.py (169 LOC)

**Purpose:** Gather lock state, GPU server health, and Postgres reachability into a single dict for `rag-cli status`; formats the output for terminal display.
**Reads:** `lock.read()` for lock state; `server_manager.box_status()` for server state; Postgres connect probe (2s timeout); `~/.rag-locks/server-port-{N}.json` state files (via server_manager).
**Writes:** nothing.
**Called by:** cli.py (`status` subcommand)
**Calls out:** (none — all via lock, server_manager, db intra-package)

---

### error_log.py (48 LOC)

**Purpose:** Append structured error entries to `src/rag/logs/errors.jsonl`; O_APPEND write is POSIX-atomic for writes under PIPE_BUF, no locking needed.
**Reads:** nothing (write-only).
**Writes:** `src/rag/logs/errors.jsonl` (one JSON line per error event).
**Called by:** server_manager.py
**Calls out:** (none — stdlib only: json, pathlib)

---

### server_lock.py (76 LOC)

**Purpose:** Per-server flock context manager (`acquire`) with `ServerBusyError` — intended for serializing concurrent HTTP calls to a single GPU server instance.
**Reads:** `~/.rag-locks/rag-server-{name}.busy.flock`; `~/.rag-locks/rag-server-{name}.busy` (JSON).
**Writes:** `~/.rag-locks/rag-server-{name}.busy.flock`; `~/.rag-locks/rag-server-{name}.busy` (atomic).
**Called by:** [] (DEAD CODE — no import callers found; verify before removing)
**Calls out:** (none — stdlib only: fcntl, json, os, pathlib)

---

## State

| Owner | State | Reads | Writes |
|---|---|---|---|
| PostgreSQL `documents` table | All indexed chunks with dense + sparse embeddings | db.py, search_primitives.py | indexer.py (insert/delete/schema), sync.py (delete via indexer primitives) |
| PostgreSQL `indexed_files` table | Per-project (collection, document) → sha256 + last_indexed_at; sync.py's change-detection ledger | sync.py (diff against current file hashes) | sync.py (upsert/delete; auto-creates table on first run) |
| `~/.rag-locks/server-port-{N}.json` | Per-process GPU server state (pid, port, model_path, model_name, mode, log_path, start_time, name); idle computed from `log_path` mtime | server_manager.py (`_watchdog_tick`, `_purge_orphans`, `find_server_url`, `box_status`), status.py | server_manager.py (`start` — written after Popen; unlinked on `stop`) |
| `~/.rag-locks/watchdog.pid` | Detached watchdog process PID for ensure-singleton spawn | server_manager.py (`_ensure_watchdog_process`) | server_manager.py (`_ensure_watchdog_process`) |
| `~/.rag-locks/rag.flock` + `rag.lock` | Global RAG mutex (flock fd) + JSON details (pid, command, started_at, heartbeat, progress) | lock.py, status.py | lock.py (`acquire`, `heartbeat`, `update_progress`) |

## Gotchas

- **splade_server.py has no Python import callers** — appears as dead code in any import grep but is the subprocess target launched by `server_manager.py`. Do not delete.
- **server_lock.py has no Python import callers** — verify dead code status before removing; may be planned for future concurrent-request serialization.
- **retriever.py re-exports format_results / format_collections / format_documents** from `formatting.py`. `cli.py` imports these from `src.rag.retriever`, not `src.rag.formatting`. Keep the import in retriever.py's INFRASTRUCTURE or cli.py breaks.
- **DEFAULT_QUERY_PREFIX** lives in `search_primitives.py`, not retriever.py — it moved with `embed_query()` during the retriever split refactor.
- **server_manager.py 1061 LOC** — well over the 400-LOC hard ceiling. Refactor candidate: watchdog loop (`_watchdog_loop`, `_watchdog_tick`, `_purge_orphans`), CLI surface (`cli_server`), and box state I/O (`_write_state_file`, `_read_state_files`) are natural extraction boundaries.
