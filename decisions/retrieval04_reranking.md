# Retrieval Step 4: Reranking

## Status Quo

**Code:** `src/rag/reranker.py`
**Model:** Qwen3-Reranker-0.6B Q8_0 via llama-server
**Server:** llama-server on port 8082, `--rerank -c 32768`
**Trigger:** Only when `rerank=True` in `search_hybrid_workflow()`. Default is `rerank=False`.
**Candidates:** Top 50 RRF candidates re-scored, top_k returned
**Score Filter:** Results below 0.3 cross-encoder score filtered out

Auto-started on first use (same lifecycle pattern as embedding server).

## Evidenz

### NOT EVALUATED

Reranking has never been measured in isolation on our data. We have no numbers for:
- With reranker vs without on same query set
- Latency impact per query
- Quality improvement (NDCG, Recall delta)

### Pipeline Optimization Paper (external)

Adding BGE cross-encoder to GTE-large pipeline: Acc@3 from 0.412 to 0.506 (+9.4pp).
Reranking bridges ~50% of the gap between 2000-char and 512-char chunking.

## Entscheidung

Qwen3-Reranker-0.6B chosen as smallest Qwen3 reranker (fast, low RAM). Default is OFF (`rerank=False`) because:
1. Adds latency (cross-encoder inference per candidate pair)
2. Reranker server uses additional GPU memory
3. Not evaluated on our data — unknown benefit

## Offene Fragen

- What is the actual NDCG improvement on our data? Run eval with `rerank=True` vs `False`.
- Latency: How much time does reranking add per query?
- Is 0.6B sufficient or would 4B/8B reranker improve quality?
- ColBERT reranking (late interaction) as alternative? VectorChord blog shows ColBERT + pgvector integration with +30% NDCG@10.

## Quellen

- RAG Collection: Pipeline_Optimization_Paper (reranking benefits: +9.4pp Acc@3)
- RAG Collection: Qwen3_Embedding_Paper (Qwen3-Reranker architecture and benchmarks)
- ColBERT + pgvector blog (VectorChord — MaxSim in PostgreSQL)
- RAG Collection: qwen3reranker (model card details)
