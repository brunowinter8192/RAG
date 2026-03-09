# Worker Report: splade-client

## Task
Create an HTTP client module for the SPLADE sparse embedding server (port 8083) and extend the DB schema + indexer to store sparse embeddings alongside dense embeddings.

## Results
- Created `src/rag/sparse_embedder.py` following the exact same INFRASTRUCTURE/ORCHESTRATOR/FUNCTIONS pattern as `embedder.py`. Includes health check, auto-start via uvicorn subprocess, and HTTP client via httpx. Extracts `sparse_vector` from the server's `{"data": [{"index": i, "sparse_vector": {...}}]}` response format.
- Modified `src/rag/indexer.py`:
  - Added import of `sparse_embed_workflow`
  - `ensure_schema()`: adds `ALTER TABLE documents ADD COLUMN IF NOT EXISTS sparse_embedding sparsevec(30522)` after table creation
  - `index_json_workflow()`: calls `sparse_embed_workflow(texts)` after `embed_workflow(texts)`, passes result to `store_chunks()`
  - Added `format_sparsevec(sparse, dimensions=30522)` helper that formats `{"indices": [...], "values": [...]}` as `'{idx:val,...}/30522'`
  - `store_chunks()`: extended with `sparse_embeddings: list[dict]` parameter, stores formatted sparsevec in `sparse_embedding` column

## Files Changed
- `src/rag/sparse_embedder.py` — NEW: HTTP client for SPLADE server, mirrors embedder.py pattern
- `src/rag/indexer.py` — MODIFIED: schema migration, sparse embedding generation and storage

## Open Issues
- None. Pyright reports a stale "Expected 3 positional arguments" diagnostic for line 60 (store_chunks call) — this is a false positive due to cached type info; the function signature and call site both use 4 arguments and are correct.
