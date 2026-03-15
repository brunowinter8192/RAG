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

256d outperforms 4096d on this small dataset. Must be validated on larger collection (SearXNG, 2337 chunks) — previous attempt crashed (Segfault exit 139). Next approach: read embeddings from DB instead of re-embedding.

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

## Entscheidung

- Qwen3-Embedding-8B: #1 MTEB Multilingual at time of selection. 4096d, 32K context.
- Q8_0 quantization: ~99.9% quality, ~9 GB. Sweet spot for M4 Pro 48GB.
- Server config (-c 2048 -np 1): Verified same performance, 30% less RAM.
- 4096d kept for now: MRL results promising but not validated on large collection.

## Offene Fragen

- MRL on large collection: Does 256d or 1024d maintain quality on 2337+ chunks?
- If MRL confirmed: HNSW index possible at 2000d (pgvector limit). Massive search speedup.
- Newer llama.cpp version: Does it fix the -ub 512 crash?
- Contextual Embeddings (Anthropic): Prepend document context to each chunk before embedding. 49-67% fewer retrieval failures claimed.

## Quellen

- RAG Collection: Qwen3_Embedding_Paper (MRL support, model architecture)
- Anthropic contextual-retrieval (Contextual Embedding concept)
- Voyage context-3 (native contextual embedding model)
- Late Chunking (Weaviate — alternative to contextual embedding)
- llama-server README: github.com/ggml-org/llama.cpp/tree/master/tools/server
