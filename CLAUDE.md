# RAG MCP Server

Hybrid RAG pipeline with dense (Qwen3) + sparse (SPLADE) embeddings, pgvector, and reranking.

## Worker Rules (Project-Specific)

**No GPU/embedding operations in workers.** Workers must NOT run scripts that embed large corpus data (embedding 2337 chunks takes 30+ min and blocks GPU). All embedding, indexing, and eval sweeps run in the main session (background commands). Workers do: code analysis, docs, research, writing plans.

## Sources

| Source | Purpose |
|--------|---------|
| pgvector | HNSW limits, index types, performance |
| Qwen3-Embedding | MRL, instruct format, dimensions |
| llama.cpp / llama-server | Embedding mode, batching, model conversion |
| SPLADE | Sparse encoder model (naver/splade-cocondenser-ensembledistil) |
| Qwen3-Reranker | Reranking architecture and usage |
| RAG Collection `llama.cppDocs` | llama.cpp API reference, server usage, changelog |

Consult via GitHub plugin or RAG search before making assumptions.

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
| `src/rag/reranker.py` | Reranker llama-server lifecycle |

## Project Structure

```
RAG/
├── server.py
├── workflow.py
├── start.sh
├── mcp-start.sh
├── requirements.txt
├── README.md                       → [Setup & External Docs](README.md)
├── src/
│   └── rag/                        → [DOCS.md](src/rag/DOCS.md)
├── dev/                            → [DOCS.md](dev/DOCS.md)
│   ├── cleanup/
│   ├── explore/
│   ├── llama_server/
│   ├── splade_benchmark/
│   └── reranker_8b/
```
