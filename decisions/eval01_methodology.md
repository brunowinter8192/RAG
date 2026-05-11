# Retrieval Eval Methodology

## Status Quo (IST)

**Files:**
- `dev/retrieval/A_retrieval_eval.py` — eval runner and report generator
- `dev/retrieval/eval_config.py` — BASELINE config + SWEEP_RANGES
- `dev/retrieval/queries_test_db.json` — 17 hand-labeled queries with expected docs + snippets
- `dev/retrieval/A_retrieval_eval_reports/` — timestamped MD reports per run

**Metrics:**
- `doc_recall` — binary: did any chunk from each expected_document appear in top-K hits?
- `snippet_recall` — binary: was each expected_snippet found as substring in any hit's content?
- `NDCG@K` — binary relevance (rel=1 if hit.document ∈ expected_documents). DCG@k = Σ (2^rel_i − 1) / log2(i+1). IDCG uses total_relevant from DB (all chunks for expected docs in collection). Capped at 1.0.
- `MRR@K` — 1/rank of first relevant hit in top-K, 0 if none.
- `Recall@K` (chunk-level) — |relevant chunks in top-K| / |total relevant chunks in collection|. Total relevant queried from DB via `src.rag.db.query_documents`.

**Test collection:** `test_db` (in `rag_test` DB) — 17 queries, 250 chunks, 7 reference papers (RAG methodology: RAGAS, RAG_Evaluation_Survey_2025, Pipeline_Optimization, Fusion_Functions_Hybrid_Retrieval, Qwen3_Embedding, SPLADE_v3, Rethinking_Chunk_Size_Long_Document).

**CLI:**
```bash
./venv/bin/python dev/retrieval/A_retrieval_eval.py --baseline [--override key=val ...]
./venv/bin/python dev/retrieval/A_retrieval_eval.py --sweep PARAM [--override key=val ...]
```
SWEEP_RANGES: mode (7 modes), top_k (5/10/20), alpha (0.5–0.9), rrf_k (30/60/90), score_threshold (0/0.3/0.5), query_prefix (True/False).

**Output:** Per-query sections with doc/snippet/rank metrics + aggregate summary table + by-query-type breakdown. Sweep generates one per-config report + a comparison table across swept values.

## Evidenz

- **RAGAS (Evaluation Framework):** prescribes context_recall + context_precision as primary retrieval metrics; binary relevance via LLM-judge is valid for small GT sets. Ground truth at document-level (expected_documents) matches the RAGAS pattern.
- **RAG Evaluation Survey 2025:** classifies retrieval metrics as document-level (MRR, MAP) vs chunk-level (Recall@K, NDCG@K). Distinguishes retrieval-only eval (our scope) from end-to-end RAG eval. NDCG@K is the most discriminative metric for ranked retrieval.
- **Pipeline Optimization Paper (arxiv:2511.22240):** uses Acc@3 and NDCG@3 on 11,000 synthetic QA pairs. Key finding: 512-char chunks outperform 2000-char by +5pp Acc@3. Provides reference point for benchmark scale; our 20-query GT is a minimal manual set.
- **Fusion Functions for Hybrid Retrieval (Bruch et al. 2023, ACM TOIS):** evaluates CC vs RRF fusion using NDCG@3 and NDCG@10. Direct methodological reference for using NDCG as the primary metric in fusion comparisons.

## Recommendation (SOLL)

Pending — needs eval execution after persisted-output threshold is calibrated (parallel worker `persisted-output-probe`) and production top-k is set. Run `--baseline` first to establish a new NDCG/MRR/Recall@K baseline for the CC α=0.8 config, then `--sweep mode` and `--sweep top_k` to fill in the missing rank-based comparison tables in retrieval03 and retrieval04.

## Offene Fragen

- **Graded relevance:** binary (relevant/not) is simpler but loses rank-within-document signal. Graded relevance (e.g. rel=2 for exact snippet match, rel=1 for doc match, rel=0 otherwise) would better distinguish partial from perfect hits.
- **Synthetic GT scaling:** Pipeline Optimization Paper uses 11k QA pairs. Our 17 queries are insufficient for statistical significance on small metric differences (< 2pp). Synthetic GT generation (LLM-based, per RAGAS) could scale to 200+ queries.
- **Train/dev/test split at n=17:** all 17 queries are currently used for both sweep comparison and final reporting — no held-out test set. At n=17 this is unavoidable; matters more if GT is scaled up.
- **Statistical significance:** sweep comparisons need paired t-test or Wilcoxon to distinguish real gains from noise. Currently reported only as raw averages. Needed before any SOLL decision on alpha, top_k, or mode.
- **Latency tracking:** eval currently measures only retrieval quality, not wall-clock latency per query. Needed for the reranker trade-off decision (doc_recall +4pp vs +2s latency).

## Quellen

Indexed in collection `RAG_reference`:
- RAGAS_Evaluation_Framework
- RAG_Evaluation_Survey_2025
- Pipeline_Optimization (arxiv:2511.22240)
- Fusion_Functions_Hybrid_Retrieval (dl.acm 10.1145/3596512)
