# HNSW Index Not Available for 4096-Dim Embeddings

## Problem

Qwen3-Embedding-8B produces 4096-dimensional vectors. pgvector HNSW index limits:

| Type | Max HNSW Dims |
|------|--------------|
| vector (32-bit) | 2000 |
| halfvec (16-bit) | 4000 |
| bit | 64000 |

4096 exceeds both vector and halfvec limits. No HNSW index possible at full dimensionality.

Source: https://github.com/pgvector/pgvector (`src/hnsw.h`, `src/hnswutils.c`)

## Current Solution

Sequential scan on the embedding column (no index). HNSW creation removed from `ensure_schema()` in `src/rag/indexer.py`.

At current scale (<10k chunks) sequential scan is sufficient. pgvector README: "if the table is small, a table scan may be faster."

Use `EXPLAIN (ANALYZE, BUFFERS)` to measure actual query performance if latency becomes a concern.

## Escape Hatch: Matryoshka Representation Learning (MRL)

Qwen3-Embedding-8B supports MRL — embeddings can be truncated to arbitrary dimensions with controlled quality loss.

Options when scale demands an index:
- Truncate to 2000 dims -> HNSW with vector type
- Truncate to 4000 dims -> HNSW with halfvec type
- Store full 4096 for search, maintain a truncated column with HNSW for candidate retrieval

Source: https://github.com/QwenLM/Qwen3-Embedding (Model Card, "MRL Support: Yes")

## History

- 2026-03-11: Bead RAG-c8q incorrectly claimed pgvector 0.8.x raised HNSW limit to 4096. False — limit unchanged since introduction. Discovered when `ensure_schema()` crashed during indexing.
