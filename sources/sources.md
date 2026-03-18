# Sources

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
