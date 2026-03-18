# Indexing Step 2: Dense Embedding

## Status Quo

**Code:** `src/rag/embedder.py`
**Model:** Qwen3-Embedding-8B Q8_0 (~9 GB GGUF)
**Server:** llama-server on port 8081
**Dimensions:** 4096d (full model output)
**MRL Support:** Yes (Matryoshka — truncate to first N dims + L2 normalize)
**Max Tokens:** 4000 (~12000 chars) per text, truncated before sending
**Query Prefix:** `Instruct: Given a search query, retrieve relevant passages that answer the query\nQuery: `

**Server Config (optimized 2026-03-15):**
```
-c 2048 -np 1 -b 4096 -ub 4096 -ngl 99
```

| Flag | Value | Why |
|------|-------|-----|
| `-c` | 2048 | Context per slot. Chunks max ~400 tokens. Saves ~30% RAM vs default 32768. |
| `-np` | 1 | Single slot. We embed sequentially, no concurrent queries during indexing. |
| `-b` | 4096 | Logical batch size. |
| `-ub` | 4096 | Physical batch size. `-ub 512` crashes llama-server v638 on Metal (Segfault after ~30 tasks). |
| `-ngl` | 99 | Full GPU offload. |

**Indexing Throughput:** ~20s per 32-chunk batch, ~1.2 chunks/sec.

## Evidenz

### MRL Dimension Sweep (Qwen3_Embedding_Paper, 15 queries, 53 chunks)

| Dims | NDCG@3 | NDCG@10 | Recall@10 |
|------|--------|---------|-----------|
| 256 | 0.4641 | 0.6152 | 0.8444 |
| 512 | 0.4207 | 0.5400 | 0.7778 |
| 1024 | 0.4387 | 0.5695 | 0.8111 |
| 2048 | 0.3810 | 0.5495 | 0.8111 |
| 4096 (full) | 0.3966 | 0.5277 | 0.7556 |

256d outperforms 4096d on this small dataset (66 chunks). Validated on larger collection below.

### MRL Dimension Sweep (searxng, 30 queries, 26088 chunks)

| Dims | NDCG@3 | NDCG@10 | Recall@10 |
|------|--------|---------|-----------|
| 256 | 0.3840 | 0.5040 | 0.6500 |
| 512 | 0.4098 | 0.5420 | 0.6944 |
| **1024** | **0.4439** | **0.5687** | **0.7278** |
| 2048 | 0.4432 | 0.5747 | 0.7278 |
| 4096 (full) | 0.4479 | 0.5619 | 0.6833 |

**1024d is the sweet spot on large collections.** Best Recall@10 (0.7278, tied with 2048d, better than full). NDCG@10 best at 1024d (0.5687 > full 0.5619). Full 4096d loses Recall — likely noise from unused dimensions hurting cosine similarity. 256d loses ~12% Recall vs 1024d — too much for production. 2048d ≈ 1024d — no gain from extra dims.

**HNSW now possible:** 1024d < 2000d pgvector HNSW limit for `vector` type.

Method: Corpus embeddings loaded from DB (no re-embedding), MRL truncation + L2 renormalization in numpy. Query embeddings via llama-server.

### Server Config Benchmark (dev/indexing_benchmark/benchmark.py)

| Config | 32 chunks | Notes |
|--------|-----------|-------|
| Original (-ub 4096, no -c, no -np) | 19.08s | 13+ GB RAM |
| Optimized (-c 2048, -np 1) | 20.37s | 9.2 GB RAM |
| With -ub 512 | CRASH | Segfault on Metal, llama.cpp v638 |

### -ub 512 Bug

llama.cpp v638 crashes on Metal/M4 Pro when `-ub 512` with Qwen3-Embedding-8B. Segfault without error log, server dies after ~30 tasks. Workaround: keep `-ub 4096`.

## Known Issue: NULL Embeddings

llama-server returns NULL vectors for chunks starting with naked `import` statements (no preceding context). Root cause: tokenizer issue with Qwen3-Embedding-8B.

**Affected:** ~2% of code-heavy chunks.
**Fix:** Prefix every chunk with `search_document: ` before embedding. Validated: all NULL chunks produce valid embeddings with prefix.
**Safety net:** `store_chunks()` in indexer.py skips NULL embeddings with warning.

Full details: Previously in `fixes/null-embeddings.md`.

## Recommendation (SOLL)

- **Change:** Embedding dimension `4096d → 1024d` — MRL Sweep on 26k chunks confirms 1024d is optimal (best Recall@10, HNSW-compatible). Migration: `UPDATE documents SET embedding = truncate_and_normalize(embedding, 1024)` — no re-embedding needed.
- **Keep:** Qwen3-Embedding-8B Q8_0 — still #1 MTEB Multilingual
- **Keep:** Server config `-c 2048 -np 1 -b 4096 -ub 4096 -ngl 99`
- **Pending:** Contextual Embeddings (Anthropic) — not evaluated

**Migration blocked:** Wait until complete pipeline eval (all decisions/ SOLL finalized). Then migrate ALL changes in one batch.

## Offene Fragen

- Newer llama.cpp version: Does it fix the -ub 512 crash?
- Contextual Embeddings (Anthropic): Prepend document context to each chunk before embedding. 49-67% fewer retrieval failures claimed.

## Quellen

- RAG Collection: Qwen3_Embedding_Paper (MRL support, model architecture)
- Anthropic contextual-retrieval (Contextual Embedding concept)
- Voyage context-3 (native contextual embedding model)
- Late Chunking (Weaviate — alternative to contextual embedding)
- llama-server README: github.com/ggml-org/llama.cpp/tree/master/tools/server
