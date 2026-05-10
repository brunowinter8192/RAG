# Retrieval Step 4: Reranking

## Status Quo (IST)

**Code:** `src/rag/reranker.py`
**Model:** Qwen3-Reranker-0.6B Q8_0 via llama-server
**Server:** llama-server on port 8082, `--rerank -c 32768`
**Trigger:** Only when `rerank=True` in `search_hybrid_workflow()`. Default is `rerank=False`.
**Candidates:** Top 50 RRF candidates re-scored, top_k returned
**Score Filter:** Results below 0.3 cross-encoder score filtered out

Auto-started on first use (same lifecycle pattern as embedding server).

## Evidenz

### Pipeline Optimization Paper (external)

Adding BGE cross-encoder to GTE-large pipeline: Acc@3 from 0.412 to 0.506 (+9.4pp).
Reranking bridges ~50% of the gap between 2000-char and 512-char chunking.

### Reranker on CC Fusion (RAG_MCP, 20 queries, 483 chunks — mixed, 2026-04-08)

| Mode | Doc Recall @10 | Snippet Recall @10 |
|---|---|---|
| CC α=0.8 | 80% | **78%** |
| CC+Rerank α=0.8 | **84%** | 77% |
| Hybrid+Rerank K=60 | **84%** | 77% |

Reranker adds +4pp Doc Recall but costs -1pp Snippet Recall. CC+Rerank = Hybrid+Rerank (reranker normalizes fusion method). For MCP tool responses where snippet quality matters more than document discovery, reranking is not recommended.

## Recommendation (SOLL)

- **Keep:** `rerank=False` as default — reranker hurts on technical docs (-8.5pp NDCG@3), which is the dominant collection type. CC+Rerank tested on RAG_MCP: +4pp Doc Recall, -1pp Snippet Recall — trade-off rejected.
- **Keep:** Qwen3-Reranker-0.6B model — adequate for academic text (+19.3pp NDCG@3)
- **Pending:** Domain-dependent rerank config (auto-enable for academic collections, disable for technical docs)
- **Pending:** Score threshold calibration (0.3 is unvalidated)
- **Pending:** Larger reranker model (4B/8B) evaluation

## Offene Fragen

- ~~What is the actual NDCG improvement on our data?~~ **RESOLVED:** -8.5pp on technical docs, +19.3pp on academic text. Domain-dependent.
- Latency: How much time does reranking add per query?
- Is 0.6B sufficient or would 4B/8B reranker improve quality?
- ColBERT reranking (late interaction) as alternative? VectorChord blog shows ColBERT + pgvector integration with +30% NDCG@10.

## Quellen

- RAG Collection: Pipeline_Optimization_Paper (reranking benefits: +9.4pp Acc@3)
- RAG Collection: Qwen3_Embedding_Paper (Qwen3-Reranker architecture and benchmarks)
- ColBERT + pgvector blog (VectorChord — MaxSim in PostgreSQL)
- RAG Collection: qwen3reranker (model card details)
- Bruch et al. 2023 "An Analysis of Fusion Functions for Hybrid Retrieval" (ACM TOIS, arXiv:2210.11934)
- RAG_MCP Fusion Sweep (dev/retrieval/A_retrieval_eval_reports/sweep_comparison_20260408_190448.md)
