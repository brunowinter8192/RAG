# RAG MCP Server

Hybrid RAG pipeline with dense (Qwen3) + sparse (SPLADE) embeddings, pgvector, and reranking.

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
