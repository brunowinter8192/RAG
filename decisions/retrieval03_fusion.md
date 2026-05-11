# Retrieval Step 3: Ranking & Fusion

## Status Quo (IST)

**Code:** `src/rag/retriever.py:search_hybrid_workflow` → calls `cc_fusion` (from `src/rag/fusion.py`, `CC_ALPHA = 0.8`)
**Method:** Convex Combination (CC) with min-max normalization
**Formula:** `score(d) = α * (dense_score - min_dense) / (max_dense - min_dense) + (1-α) * (sparse_score / max_sparse)`
**α parameter:** 0.8 (`CC_ALPHA` constant in `fusion.py`)
**Input:** Top 50 Dense + Top 50 Sparse candidates
**Output:** Fused ranking, top_k returned

`cc_fusion` is the live default in `search_hybrid_workflow()`. `rrf_fusion` is retained in `fusion.py` as a reference implementation but is not called from the workflow. `search_workflow()` (pure dense) returns dense results directly without fusion.

### Code-Drift-Closure 2026-05-11

`cc_fusion` in `fusion.py` was previously max-only normalization (`score / max_vec`) despite the IST claim of "min-max normalization". Commit `309c018` introduced proper min-max for the dense branch: `(score - min_vec) / range_vec` with `range_vec == 0 → norm = 1.0` fallback. Sparse branch (`score / max_kw`) unchanged — SPLADE scores are non-negative, max-only is correct there. IST formula and statement now match the code.

## Evidenz

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

Script: pre-A_retrieval_eval.py eval harness (not committed to repo — non-reproducible; data preserved in report).
Report: `dev/retrieval/A_retrieval_eval_reports/sweep_comparison_20260408_190448.md`

## Recommendation (SOLL)

- **Keep:** CC α=0.8 (Convex Combination with min-max normalization). CC outperforms RRF on Snippet Recall (+3pp) while matching Doc Recall. Based on Bruch et al. 2023 ("An Analysis of Fusion Functions for Hybrid Retrieval"), confirmed on RAG_MCP collection (2026-04-08, re-confirmed 2026-04-28). `cc_fusion` is the active default; `rrf_fusion` retained in `fusion.py` as reference.
- **Keep:** Hybrid as separate MCP tool (`search_hybrid`), not default search path
- **Keep:** Rerank=False as default — reranker costs 1pp Snippet Recall and adds latency. Only +4pp Doc Recall does not justify the trade-off for MCP tool responses where snippet quality matters more.

## Offene Fragen

- Should hybrid be the default search? Currently only via explicit `search_hybrid` tool call. Evidence says: only if Sparse component is fixed.
- Weighted RRF: Give Dense higher weight than Sparse? Not standard RRF but could compensate for weak Sparse.

## Quellen

- Anthropic contextual-retrieval (RRF for hybrid retrieval)
- RAG Collection: Pipeline_Optimization (two-stage retrieval findings)
- Bruch et al. 2023 "An Analysis of Fusion Functions for Hybrid Retrieval" (ACM TOIS, arXiv:2210.11934)
