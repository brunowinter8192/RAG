# Worker Report: prefix-fix

## Task
Fix Qwen3-Embedding prefix handling: documents must be indexed as plain text (no prefix), queries must use the `Instruct: ... Query: ` format.

## Results
- `embedder.py`: `embed_workflow()` and `generate_embeddings()` now accept optional `prefix: str | None = None`. When `None`, texts are sent as-is. When set, prefix is prepended to each text. The old hardcoded `search_document: ` prefix is removed.
- `retriever.py`: Added constant `DEFAULT_QUERY_PREFIX` with the Qwen3 instruct format. `embed_query()` now passes this prefix to `embed_workflow()`.
- `indexer.py` unchanged — already calls `embed_workflow(texts)` without prefix, which is now correct for document indexing.

## Files Changed
- `src/rag/embedder.py` — Added `prefix` param to `embed_workflow()` and `generate_embeddings()`; removed hardcoded `search_document:` prefix
- `src/rag/retriever.py` — Added `DEFAULT_QUERY_PREFIX` constant; updated `embed_query()` to pass it

## Open Issues
None. Clean implementation matching the spec.
