# Worker Report: splade-retriever

## Task
Replace BM25 with SPLADE in the hybrid search path by adding a `splade_search()` function and wiring it into `search_hybrid_workflow()`.

## Results
- Added `from .sparse_embedder import sparse_embed_workflow` import to INFRASTRUCTURE section
- Added `splade_search()` function after `_bm25_query` in the FUNCTIONS section — calls `sparse_embed_workflow`, formats the sparse vector as `{idx:val,...}/30522`, queries `sparse_embedding <=> %s::sparsevec` with cosine distance, returns same dict structure as `search_vectors()` and `bm25_search()`
- Changed one line in `search_hybrid_workflow()`: `bm25_search(...)` → `splade_search(...)`
- Updated log message: `bm25=` → `splade=`
- `bm25_search()` and `_bm25_query()` untouched — still used by `search_keyword_workflow`

## Files Changed
- `src/rag/retriever.py` — added import, added `splade_search()`, wired into `search_hybrid_workflow()`

## Open Issues
None.
