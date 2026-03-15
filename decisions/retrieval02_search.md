# Retrieval Step 2: Vector Search

## Status Quo

**Code:** `src/rag/retriever.py:search_vectors()`, `splade_search()`, `bm25_search()`
**Dense Search:** pgvector cosine distance (`embedding <=> query::vector`)
**Sparse Search:** pgvector sparsevec cosine distance (`sparse_embedding <=> query::sparsevec`)
**BM25 Search:** PostgreSQL tsvector full-text search (`ts_rank`)
**Index:** Sequential scan (no HNSW). GIN index on tsvector column.

**Candidates:** Top 50 per search method (HYBRID_CANDIDATES = 50)

### Why No HNSW Index

pgvector HNSW supports max 2000 dims for `vector` type, max 4000 dims for `halfvec`. Our embeddings are 4096d `vector` — exceeds both limits.

Options to enable HNSW:
1. MRL to 2000d or less → standard HNSW
2. MRL to 4000d or less → halfvec HNSW
3. pgvector future version raises limit

## Evidenz

No isolated search benchmark. Search performance is measured implicitly through eval suite.

At current scale (~7000 chunks across all collections), sequential scan is fast enough (<100ms per query). HNSW becomes critical at 100k+ chunks.

## Entscheidung

Sequential scan accepted for current scale. HNSW blocked by 4096d embedding dimension. MRL evaluation will determine if we can reduce dimensions.

## Offene Fragen

- pgvector 0.8 iterative scans: 5.7x faster for filtered searches. Are we on 0.8? (Yes, 0.8.2)
- HNSW tuning (m, ef_construction, ef_search) — relevant only after MRL enables it
- At what collection size does sequential scan become unacceptable? Need to benchmark.

## Quellen

- AWS pgvector 0.8 blog (iterative scans, filtered search improvements)
- HNSW at scale (TDS — degradation patterns at scale)
- CrunchyData HNSW tuning guide (m, ef_construction, ef_search)
- ColBERT + pgvector (VectorChord — MaxSim in PostgreSQL)
