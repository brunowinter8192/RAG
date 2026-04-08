# Retrieval Step 3: Ranking & Fusion

## Status Quo (IST)

**Code:** `src/rag/retriever.py:rrf_fusion()`
**Method:** Reciprocal Rank Fusion (RRF)
**Formula:** `score(d) = sum(1 / (K + rank_i(d)))` across all result lists
**K parameter:** 60 (standard, RRF_K constant)
**Input:** Top 50 Dense + Top 50 Sparse candidates
**Output:** Fused ranking, top_k returned

RRF is used only in `search_hybrid_workflow()`. The `search_workflow()` (pure dense) returns dense results directly without fusion.

## Evidenz

### SearXNG (30 queries, 26088 chunks — technical docs, 2026-03-18)

| Retriever | NDCG@3 | NDCG@10 | Recall@10 |
|---|---|---|---|
| Dense (full) | **0.4479** | **0.5619** | **0.6833** |
| Hybrid (RRF K=60) | 0.2469 | 0.3666 | 0.5167 |
| Hybrid+Rerank | 0.3967 | 0.5052 | 0.6444 |
| Sparse (SPLADE++) | 0.0000 | 0.0000 | 0.0000 |

**Hybrid is WORSE than Dense alone.** SPLADE is completely out-of-domain on technical docs (zero matches in 26k chunks). RRF fusion degrades the Dense ranking by mixing in noise. Reranker partially recovers Hybrid (0.247→0.397 NDCG@3) but still worse than pure Dense.

### Qwen3 Paper (15 queries, 66 chunks — academic text, 2026-03-18)

| Retriever | NDCG@3 | NDCG@10 | Recall@10 |
|---|---|---|---|
| Dense (full) | 0.3605 | 0.5102 | 0.7333 |
| Hybrid (RRF K=60) | 0.4168 | 0.5369 | 0.8000 |
| **Hybrid+Rerank** | **0.5538** | **0.6620** | **0.8556** |
| Sparse (SPLADE++) | 0.4273 | 0.5273 | 0.7333 |

On academic text, Hybrid outperforms Dense on Recall@10 (0.80 vs 0.73). Hybrid+Rerank is best overall. SPLADE contributes meaningfully on in-domain text.

### RAG_MCP Fusion Sweep (20 queries, 483 chunks — mixed academic+technical, 2026-04-08)

| Mode | Params | Doc Recall @10 | Snippet Recall @10 |
|---|---|---|---|
| Dense | - | 77% | 72% |
| Hybrid (RRF) | K=30 | 80% | 75% |
| Hybrid (RRF) | K=60 | 80% | 75% |
| Hybrid (RRF) | K=90 | 80% | 75% |
| CC | α=0.5 | 80% | 73% |
| CC | α=0.6 | 80% | 73% |
| CC | α=0.7 | 80% | 75% |
| **CC** | **α=0.8** | **80%** | **78%** |
| CC | α=0.9 | 80% | 72% |
| CC+Rerank | α=0.8 | 84% | 77% |
| Hybrid+Rerank | K=60 | 84% | 77% |

**CC α=0.8 is best without reranking** (highest Snippet Recall). RRF is K-insensitive on this collection. CC+Rerank and Hybrid+Rerank converge to same result (reranker normalizes input). Reranker adds +4pp Doc Recall but costs -1pp Snippet Recall and adds ~2s latency per query.

## Recommendation (SOLL)

- **Change:** RRF K=60 → CC α=0.8 (Convex Combination with min-max normalization). CC outperforms RRF on Snippet Recall (+3pp) while matching Doc Recall. Based on Bruch et al. 2023 ("An Analysis of Fusion Functions for Hybrid Retrieval") and confirmed on RAG_MCP collection.
- **Keep:** Hybrid as separate MCP tool (`search_hybrid`), not default search path
- **Keep:** Rerank=False as default — reranker costs 1pp Snippet Recall and adds latency. Only +4pp Doc Recall does not justify the trade-off for MCP tool responses where snippet quality matters more.

## Offene Fragen

- Should hybrid be the default search? Currently only via explicit `search_hybrid` tool call. Evidence says: only if Sparse component is fixed.
- Weighted RRF: Give Dense higher weight than Sparse? Not standard RRF but could compensate for weak Sparse.

## Quellen

- Anthropic contextual-retrieval (RRF for hybrid retrieval)
- RAG Collection: Pipeline_Optimization_Paper (two-stage retrieval findings)
- Bruch et al. 2023 "An Analysis of Fusion Functions for Hybrid Retrieval" (ACM TOIS, arXiv:2210.11934)
- RAG_MCP Fusion Sweep (dev/retrieval/A_retrieval_eval_reports/sweep_comparison_20260408_190448.md)
