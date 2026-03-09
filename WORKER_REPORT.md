# Worker Report: splade-server

## Task
Create a standalone FastAPI server that generates SPLADE sparse embeddings via `naver/splade-cocondenser-ensembledistil`, exposing `/health` and `POST /v1/sparse-embeddings` on port 8083.

## Results

Verified the actual `SparseEncoder.encode()` API before writing code:
- Returns a `list[torch.Tensor]` with `layout=torch.sparse_coo`
- Indices extracted via `t.coalesce().indices().squeeze(0).tolist()`
- Values extracted via `t.values().tolist()`

Model is loaded once at module level (not per request). Server follows the project's INFRASTRUCTURE → ORCHESTRATOR → FUNCTIONS structure, matching the pattern in `reranker.py` and `embedder.py`.

Added `fastapi>=0.110.0`, `uvicorn>=0.29.0`, `sentence-transformers>=3.0.0` to `requirements.txt` (they were missing).

## Files Changed

- `src/rag/splade_server.py` — New FastAPI server with `/health` and `POST /v1/sparse-embeddings`
- `scripts/start_splade_server.sh` — Bash script to start the server via uvicorn (executable)
- `requirements.txt` — Added fastapi, uvicorn, sentence-transformers

## Open Issues

- `fastapi`, `uvicorn`, and `pydantic` are not yet installed in the project venv. Run `pip install -r requirements.txt` before starting the server.
- Pyright shows import errors for these packages (expected until installed).
