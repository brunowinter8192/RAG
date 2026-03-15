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

### SearXNG (30 queries, 2337 chunks)

| Retriever | NDCG@3 | Recall@10 |
|-----------|--------|-----------|
| Dense only | 0.465 | 0.678 |
| Hybrid (RRF K=60) | 0.298 | 0.656 |
| Sparse only | 0.256 | 0.478 |

**Hybrid is WORSE than Dense alone.** RRF merges two rankings, but when Sparse anti-correlates with relevance (as on SearXNG technical docs), fusion degrades the Dense ranking.

### Qwen3 Paper (15 queries, 53 chunks)

| Retriever | NDCG@3 | Recall@10 |
|-----------|--------|-----------|
| Hybrid (RRF K=60) | 0.421 | 0.822 |
| Sparse | 0.416 | 0.733 |
| Dense | 0.397 | 0.756 |

On small academic dataset, Hybrid is best. Sparse is competitive with Dense. RRF fusion adds value when both components contribute.

## Entscheidung

RRF K=60 is the standard value from the original RRF paper. No tuning done. Hybrid search exists as separate MCP tool (`search_hybrid`) — not the default search path.

## Offene Fragen

- RRF K tuning: Would K=30 or K=80 change results significantly? Eval suite supports `--rrf-k` flag.
- Should hybrid be the default search? Currently only via explicit `search_hybrid` tool call. Evidence says: only if Sparse component is fixed.
- Convex Combination (CC) as alternative to RRF? AutoRAG supports both.
- Weighted RRF: Give Dense higher weight than Sparse? Not standard RRF but could compensate for weak Sparse.

## Quellen

- Anthropic contextual-retrieval (RRF for hybrid retrieval)
- RAG Collection: Pipeline_Optimization_Paper (two-stage retrieval findings)
