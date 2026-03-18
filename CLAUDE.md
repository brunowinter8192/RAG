# RAG MCP Server

Hybrid RAG pipeline with dense (Qwen3) + sparse (SPLADE) embeddings, pgvector, and reranking.

## Sources

See [sources/sources.md](sources/sources.md).

## Pipeline Components

### Indexing Pipeline (offline, batch)

| Component | Implementation | Config |
|-----------|---------------|--------|
| **Chunking** | Recursive character split (paragraph → sentence → word) | 1000 chars, 200 overlap |
| **Dense Embedding** | Qwen3-Embedding-8B Q8_0 via llama-server | 4096d, port 8081, -c 2048 -np 1 |
| **Sparse Embedding** | SPLADE++ (cocondenser-ensembledistil) via FastAPI | 30522d sparse, port 8083 |
| **Storage** | pgvector (PostgreSQL 18, vector + sparsevec) | Sequential scan (kein HNSW bei 4096d) |

### Retrieval Pipeline (online, per query)

| Component | Implementation | Config |
|-----------|---------------|--------|
| **Query Embedding** | Same as Dense + Sparse above | Instruct prefix for Dense |
| **Dense Search** | pgvector cosine distance | top 50 candidates |
| **Sparse Search** | SPLADE cosine on sparsevec | top 50 candidates |
| **Fusion** | Reciprocal Rank Fusion (RRF) | K=60 |
| **Reranking** | Qwen3-Reranker-0.6B via llama-server | port 8082, cross-encoder |
| **Delivery** | MCP Tools (FastMCP) | search, search_hybrid, search_keyword, read_document |

### Key Files

| File | Component |
|------|-----------|
| `src/rag/chunker.py` | Chunking |
| `src/rag/embedder.py` | Dense Embedding + llama-server lifecycle |
| `src/rag/sparse_embedder.py` | Sparse Embedding + SPLADE server lifecycle |
| `src/rag/splade_server.py` | SPLADE FastAPI server |
| `src/rag/indexer.py` | Storage (pgvector inserts, schema, parallel embed) |
| `src/rag/retriever.py` | All retrieval (search, fusion, reranking, formatting) |
| `src/rag/reranker.py` | Reranker HTTP client |
| `src/rag/server_manager.py` | GPU server lifecycle (start/stop/status/idle-timeout) |

## Project Structure

```
RAG/
├── server.py
├── workflow.py
├── start.sh
├── mcp-start.sh
├── requirements.txt
├── DOCS.md                         → [Root Module Docs](DOCS.md)
├── README.md                       → [Setup & External Docs](README.md)
├── sources/
│   └── sources.md                  → [Sources & References](sources/sources.md)
├── decisions/                      → Pipeline decision records (rationale per implementation choice)
│   ├── index01_chunking.md
│   ├── index02_dense_embedding.md
│   ├── index03_sparse_embedding.md
│   ├── retrieval01_query_embedding.md
│   ├── retrieval02_search.md
│   ├── retrieval03_fusion.md
│   └── retrieval04_reranking.md
├── data/
│   └── documents/                  → Document folders per collection (raw.md, cleaned.md, chunks.json)
├── scripts/                        → Shell scripts
├── known_limitations/              → Known system limitations (hnsw_4096_dims.md)
├── src/
│   └── rag/                        → [DOCS.md](src/rag/DOCS.md)
├── dev/                            → [DOCS.md](dev/DOCS.md)
│   ├── cleanup/                    → [DOCS.md](dev/cleanup/DOCS.md)
│   ├── indexing/                   → [DOCS.md](dev/indexing/DOCS.md)
│   │   ├── chunking_eval/
│   │   ├── embedding_benchmark/
│   │   ├── indexing_benchmark/
│   │   └── llama_server/           → [DOCS.md](dev/indexing/llama_server/DOCS.md)
│   └── retrieval/                  → [DOCS.md](dev/retrieval/DOCS.md)
│       ├── eval/                   → [DOCS.md](dev/retrieval/eval/DOCS.md)
│       └── reranker_8b/
```
