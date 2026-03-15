# RAG MCP Server

Hybrid RAG pipeline with dense (Qwen3) + sparse (SPLADE) embeddings, pgvector, and reranking.

## Worker Rules (Project-Specific)

**No GPU/embedding operations in workers.** Workers must NOT run scripts that embed large corpus data (embedding 2337 chunks takes 30+ min and blocks GPU). All embedding, indexing, and eval sweeps run in the main session (background commands). Workers do: code analysis, docs, research, writing plans.

## Sources

**RAG Collection `RAG_MCP`** — Indexed papers for this project. Search with `mcp__rag__search_hybrid(collection="RAG_MCP")`.

| Source | Type | Pipeline Steps | Status |
|--------|------|---------------|--------|
| Pipeline_Optimization_Paper | Paper | index01, retrieval03, retrieval04 | Indexed (RAG_MCP) |
| Qwen3_Embedding_Paper | Paper | index02, retrieval01 | Indexed (RAG_MCP) |
| SPLADE_v3_Paper | Paper | index03 | Indexed (RAG_MCP) |
| anthropic.com/news/contextual-retrieval | Web | index01, index02, index03, retrieval01, retrieval03 | Not indexed |
| platform.claude.com/.../contextual-embeddings-guide | Web | index02 | Not indexed |
| blog.vectorchord.ai/.../colbert-rerank-in-postgresql | Web | retrieval02, retrieval04 | Not indexed |
| aws.amazon.com/.../pgvector-0-8-0 | Web | retrieval02 | Not indexed |
| blog.voyageai.com/voyage-context-3 | Web | index02 | Not indexed |
| developer.nvidia.com/.../chunking-strategy | Web | index01 | Not indexed |
| research.trychroma.com/evaluating-chunking | Web | index01 | Not indexed |
| superlinked.com/.../chunking-methods | Web | index01, retrieval04 | Not indexed |
| towardsdatascience.com/hnsw-at-scale | Web | retrieval02 | Not indexed |
| medium.com/.../late-chunking-vs-contextual-retrieval | Web | index01, index02 | Not indexed |
| docs.together.ai/.../contextual-rag | Web | index02, retrieval04 | Not indexed |
| zilliz.com/.../hyde | Web | retrieval01 | Not indexed |
| docs.haystack.deepset.ai/.../hyde | Web | retrieval01 | Not indexed |
| weaviate.io/blog/late-chunking | Web | index02 | Not indexed |
| crunchydata.com/.../hnsw-indexes | Web | retrieval02 | Not indexed |

**Other RAG Collections:** `llama.cppDocs` (llama-server API reference), `SearXNG_Docs` (SearXNG documentation)

Consult via RAG search or GitHub plugin before making assumptions. Pipeline step references match `decisions/` files.

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
├── decisions/                      → Pipeline decisions & evidence per step
│   ├── index01_chunking.md
│   ├── index02_dense_embedding.md
│   ├── index03_sparse_embedding.md
│   ├── retrieval01_query_embedding.md
│   ├── retrieval02_search.md
│   ├── retrieval03_fusion.md
│   └── retrieval04_reranking.md
├── src/
│   └── rag/                        → [DOCS.md](src/rag/DOCS.md)
├── dev/                            → [DOCS.md](dev/DOCS.md)
│   ├── cleanup/
│   ├── explore/
│   ├── llama_server/
│   ├── splade_benchmark/
│   └── reranker_8b/
```
