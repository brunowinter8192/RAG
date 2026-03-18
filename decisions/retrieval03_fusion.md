# Retrieval Step 3: Ranking & Fusion

## Status Quo

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

## Recommendation (SOLL)

- **Keep:** RRF K=60 (standard value, no evidence for tuning)
- **Keep:** Hybrid as separate MCP tool (`search_hybrid`), not default search path — Dense-only outperforms Hybrid on technical docs
- **Pending:** RRF K tuning (eval_runner supports `--rrf-k` flag, not yet swept)
- **Pending:** Convex Combination (CC) as RRF alternative

## Offene Fragen

- RRF K tuning: Would K=30 or K=80 change results significantly? Eval suite supports `--rrf-k` flag.
- Should hybrid be the default search? Currently only via explicit `search_hybrid` tool call. Evidence says: only if Sparse component is fixed.
- Convex Combination (CC) as alternative to RRF? AutoRAG supports both.
- Weighted RRF: Give Dense higher weight than Sparse? Not standard RRF but could compensate for weak Sparse.

## Quellen

- Anthropic contextual-retrieval (RRF for hybrid retrieval)
- RAG Collection: Pipeline_Optimization_Paper (two-stage retrieval findings)
