# RAG MCP Server

Hybrid RAG pipeline with dense (Qwen3) + sparse (SPLADE) embeddings, pgvector, and reranking.

## Worker Rules (Project-Specific)

**No GPU/embedding operations in workers.** Workers must NOT run scripts that embed large corpus data (embedding 2337 chunks takes 30+ min and blocks GPU). All embedding, indexing, and eval sweeps run in the main session (background commands). Workers do: code analysis, docs, research, writing plans.

## Sources

**RAG Collection `RAG_MCP`** — Knowledge base for this project. Search with `mcp__rag__search_hybrid(collection="RAG_MCP")`.

| Source | Domain | Type | Pipeline Steps | Status |
|--------|--------|------|---------------|--------|
| Pipeline Optimization Paper | arxiv.org | Paper | index01, retrieval03, retrieval04 | Indexed |
| Qwen3 Embedding Paper | arxiv.org | Paper | index02, retrieval01 | Indexed |
| SPLADE v3 Paper | arxiv.org | Paper | index03 | Indexed |
| Contextual Retrieval (2 articles) | anthropic.com | Web | index01, index02, index03, retrieval01, retrieval03 | Indexed |
| Embeddings Guide | platform.claude.com | Web | index02 | Indexed |
| ColBERT Rerank Tutorial | docs.vectorchord.ai | Web | retrieval02, retrieval04 | Indexed |
| pgvector 0.8.0 Walkthrough | thenile.dev | Web | retrieval02 | Indexed |
| Evaluating Chunking + Context Rot | research.trychroma.com | Web | index01 | Indexed |
| Chunking Strategies Guide | zilliz.com | Web | index01, retrieval04 | Indexed |
| HNSW Algorithm Guide | pinecone.io | Web | retrieval02 | Indexed |
| Contextual RAG + RAG Workflow + Rerankers + Embeddings (4 articles) | docs.together.ai | Web | index02, retrieval04 | Indexed |
| HyDE + Advanced RAG (2 articles) | docs.haystack.deepset.ai | Web | retrieval01 | Indexed |
| Late Chunking | weaviate.io | Web | index02 | Indexed |
| HNSW Indexes + pgvector Performance + Scaling Vectors (3 articles) | crunchydata.com | Web | retrieval02 | Indexed |
| Reranker Docs | docs.voyageai.com | Web | retrieval04 | Indexed |
| Qwen3-Embedding Model Card + Eval Code | github.com (QwenLM/Qwen3-Embedding) | GitHub | index02, retrieval04 | Via GitHub Plugin |
| Reranker Threshold Calibration | reddit.com (r/Rag) | Reddit | retrieval04 | Via Reddit Plugin |
| MRL Sweet Spot Analysis (Qwen3-0.6B) | medium.com (@yashasvimantha) | Web | index02 | Indexed |
| Qwen3 vs BGE-M3 Comparative Analysis | medium.com (@mrAryanKumar) | Web | index01, index02 | Indexed |
| Rethinking Chunk Size for Long-Document Retrieval | arxiv.org (2505.21700) | Paper | index01 | Indexed |
| Beyond Chunk-Then-Embed: Chunking Taxonomy | arxiv.org (2602.16974) | Paper | index01 | Indexed |
| Analysis of Fusion Functions for Hybrid Retrieval | dl.acm.org (10.1145/3596512) | Paper | retrieval03 | Indexed |
| Semantic Reranking (Cross-Encoder Thresholds) | elastic.co | Web | retrieval04 | Reference |

**Other RAG Collections:** `searxng` (SearXNG project docs), `TradBot` (trading bot docs)

Consult via RAG search or GitHub plugin before making assumptions. Pipeline step references match `decisions/` files.

## Startup

**MCP Server** starts automatically via `mcp-start.sh` (PostgreSQL + FastMCP). Supports `list_collections`, `list_documents`, `read_document` without GPU servers.

**GPU Servers** auto-start on demand via `server_manager.py` when search/index operations are called. Auto-stop after 15 minutes idle (`IDLE_TIMEOUT=900`, env `RAG_SERVER_IDLE_TIMEOUT`). Manual control:

```bash
./venv/bin/python workflow.py server status           # Check all servers
./venv/bin/python workflow.py server start             # Start all
./venv/bin/python workflow.py server stop              # Stop all
./venv/bin/python workflow.py server restart splade    # Restart one
./start.sh                                            # PostgreSQL + all GPU servers
```

Server configs (ports, model paths, flags) are defined in `src/rag/server_manager.py` — single source of truth.

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
