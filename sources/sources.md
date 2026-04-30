# Sources

**RAG Collection `RAG_reference`** — Knowledge base for this project. Search with `mcp__rag__search_hybrid(collection="RAG_reference")`.

| Source | Domain | Type | Pipeline Steps | Status |
|--------|--------|------|---------------|--------|
| Pipeline Optimization Paper | arxiv.org (2511.22240) | Paper | index01, retrieval03, retrieval04 | Indexed |
| Qwen3 Embedding Paper | arxiv.org (2506.05176) | Paper | index02, retrieval01 | Indexed |
| SPLADE v3 Paper | arxiv.org (2403.06789) | Paper | index03 | Indexed |
| Rethinking Chunk Size for Long-Document Retrieval | arxiv.org (2505.21700) | Paper | index01 | Indexed |
| Beyond Chunk-Then-Embed: Chunking Taxonomy | arxiv.org (2602.16974) | Paper | index01 | Indexed |
| Analysis of Fusion Functions for Hybrid Retrieval | dl.acm.org (10.1145/3596512) | Paper | retrieval03 | Indexed |
| Adaptive Chunking: Optimizing Chunking-Method Selection for RAG | arxiv.org (2603.25333) | Paper | index01 | Indexed |
| Reconstructing Context: Evaluating Advanced Chunking Strategies | arxiv.org (2504.19754) | Paper | index01, index02 | Indexed |
| Evaluating Chunking Strategies for RAG in Oil/Gas Enterprise Documents | arxiv.org (2603.24556) | Paper | index01 | Indexed |
| 2D Matryoshka Training for Information Retrieval | arxiv.org (2411.17299) | Paper | index02 | Indexed |
| Empirical Evaluation of PDF Parsing and Chunking for Financial QA with RAG | arxiv.org (2604.12047) | Paper | index01 | Indexed |
| Contextual Retrieval (2 articles) | anthropic.com | Web | index01, index02, index03, retrieval01, retrieval03 | Referenced |
| Embeddings Guide | platform.claude.com | Web | index02 | Referenced |
| ColBERT Rerank Tutorial | docs.vectorchord.ai | Web | retrieval02, retrieval04 | Referenced |
| pgvector 0.8.0 Walkthrough | thenile.dev | Web | retrieval02 | Referenced |
| Evaluating Chunking + Context Rot | research.trychroma.com | Web | index01 | Referenced |
| Chunking Strategies Guide | zilliz.com | Web | index01, retrieval04 | Referenced |
| HNSW Algorithm Guide | pinecone.io | Web | retrieval02 | Referenced |
| Contextual RAG + RAG Workflow + Rerankers + Embeddings (4 articles) | docs.together.ai | Web | index02, retrieval04 | Referenced |
| HyDE + Advanced RAG (2 articles) | docs.haystack.deepset.ai | Web | retrieval01 | Referenced |
| Late Chunking | weaviate.io | Web | index02 | Referenced |
| HNSW Indexes + pgvector Performance + Scaling Vectors (3 articles) | crunchydata.com | Web | retrieval02 | Referenced |
| Reranker Docs | docs.voyageai.com | Web | retrieval04 | Referenced |
| MRL Sweet Spot Analysis (Qwen3-0.6B) | medium.com (@yashasvimantha) | Web | index02 | Referenced |
| Qwen3 vs BGE-M3 Comparative Analysis | medium.com (@mrAryanKumar) | Web | index01, index02 | Referenced |
| Qwen3-Embedding Model Card + Eval Code | github.com (QwenLM/Qwen3-Embedding) | GitHub | index02, retrieval04 | Via GitHub Plugin |
| Reranker Threshold Calibration | reddit.com (r/Rag) | Reddit | retrieval04 | Via Reddit Plugin |
| Semantic Reranking (Cross-Encoder Thresholds) | elastic.co | Web | retrieval04 | Reference |
| Reddit: pgvector SOTA Discussion (14 threads) | reddit.com | Forum | index04 | Referenced |
| Reddit: Embedding Model SOTA (15 threads) | reddit.com | Forum | index02 | Referenced |
| Reddit: Chunking for Decoder Models (10 threads) | reddit.com | Forum | index01 | Referenced |
| pgvector GitHub Releases | github.com (pgvector/pgvector) | Repo | index04 | Referenced |
| dep-tree (3D Code Dependency Visualizer) | github.com (gabotechs/dep-tree) | Repo | — (tooling, not pipeline) | Referenced |
| A Systematic Analysis of Chunking Strategies for Reliable QA | arxiv.org (2601.14123) | Paper | index01 | Referenced |
| HiChunk: Evaluating and Enhancing RAG with Hierarchical Chunking | arxiv.org (2509.11552) | Paper | index01 | Referenced |
| The Chronicles of RAG: The Retriever, the Chunk and the Generator | arxiv.org (2401.07883) | Paper | index01, retrieval03 | Referenced |
| Toward General Semantic Chunking: Discriminative Framework for Ultra-Long Documents | arxiv.org (2602.23370) | Paper | index01 | Referenced |
| cAST: Enhancing Code RAG with Structural Chunking via AST | arxiv.org (2506.15655) | Paper | index01 | Referenced |
| Relative Positioning Based Code Chunking for Repository-Level Code Completion | arxiv.org (2510.08610) | Paper | index01 | Referenced |
| Can LLMs Replace Humans During Code Chunking? | arxiv.org (2506.19897) | Paper | index01 | Referenced |
| Semantic Source Code Segmentation using Small and Large Language Models | arxiv.org (2507.08992) | Paper | index01 | Referenced |
| Financial Report Chunking for Effective RAG | arxiv.org (2402.05131) | Paper | index01 | Referenced |
| Late Chunking (original paper) | arxiv.org (2409.04701) | Paper | index02 | Referenced |
| Is Semantic Chunking Worth the Computational Cost? | arxiv.org (2410.13070) | Paper | index01 | Referenced |
| Hierarchical Text Segmentation Chunking | arxiv.org (2507.09935) | Paper | index01 | Referenced |
| Contextual Document Embeddings | arxiv.org (2410.02525) | Paper | index02 | Referenced |
| Context is Gold (ConTEB benchmark + InSeNT training) | arxiv.org (2505.24782) | Paper | index02 | Referenced |

Consult via RAG search or GitHub plugin before making assumptions. Pipeline step references match `decisions/` files.

**Status legend:**
- `Indexed` — content searchable in current `RAG_reference` collection
- `Referenced` — consulted historically; no longer in active RAG index (kept for attribution)
- `Via <Plugin>` — accessible through plugin tooling, not local index
- `Reference` — single-source quote, no full content stored
