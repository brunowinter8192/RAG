# Retrieval Eval Methodology

## Status Quo (IST)

**Files:**
- `dev/retrieval/A_retrieval_eval.py` — eval runner and report generator
- `dev/retrieval/eval_config.py` — BASELINE config (includes `collection` key) + SWEEP_RANGES
- `dev/retrieval/queries_test_db.json` — 17 queries, ground truth for `test_db` (chunk_size 2000/400)
- `dev/retrieval/queries_test_db_2.json` — same 17 queries, chunk_indices for `test_db_2` (chunk_size 1000/200)
- `dev/retrieval/queries_test_db_3.json` — same 17 queries, chunk_indices for `test_db_3` (chunk_size 512/100)
- `dev/retrieval/A_retrieval_eval_reports/` — timestamped MD reports per run

**Ground truth schema:** Per query, `expected_chunks: [{document, chunk_index, identifying_quote}]` — binary relevance by construction. Each entry is a chunk from which the query was formulated; `identifying_quote` is a verbatim substring unique within that document across all three collection variants. Supersedes the former flat `expected_snippets` approach.

**Metrics:**
- `NDCG@K` (primary) — binary relevance: rel=1 iff `(hit.document, hit.chunk_index) ∈ expected_chunks`. `total_relevant = len(expected_chunks)` per query. DCG@k = Σ (2^rel_i − 1) / log2(i+1), capped at 1.0.
- `MRR@K` — 1/rank of first `expected_chunks` hit in top-K, 0 if none.
- `Recall@K` (chunk-level) — |expected_chunks in top-K| / |expected_chunks total|.
- `snippet_recall` (sanity check) — per `identifying_quote` in expected_chunks, found as case-insensitive substring in any top-K hit's content? Fraction found. Detects wording drift but secondary to chunk-level metrics.
- `doc_recall` (diagnostic) — per `expected_documents`, any chunk from it in top-K? Used to distinguish "doc found, wrong chunk" from "doc not found at all".

**Drift-detector:** `_verify_drift()` runs at eval startup — for each `expected_chunks` entry, asserts the `identifying_quote` IS a substring of `content` at `(collection, document, chunk_index)` via DB SELECT. Any miss → eval prints error and exits 1. Catches re-indexing with different chunk boundaries without silent metric degradation.

**Multi-collection support:** `--override collection=test_db_2` switches both the active collection AND auto-selects `queries_test_db_2.json`. `--queries <path>` overrides auto-selection. `--collection X` is shorthand for `--override collection=X`.

**Test collections:** all in `rag_test` DB, same 7 RAG-methodology source papers.
- `test_db` — 250 chunks (chunk_size 2000, overlap 400)
- `test_db_2` — 511 chunks (chunk_size 1000, overlap 200)
- `test_db_3` — 1027 chunks (chunk_size 512, overlap 100)

**CLI:**
```bash
./venv/bin/python dev/retrieval/A_retrieval_eval.py --baseline [--override key=val ...]
./venv/bin/python dev/retrieval/A_retrieval_eval.py --baseline --override collection=test_db_2
./venv/bin/python dev/retrieval/A_retrieval_eval.py --sweep PARAM [--override key=val ...]
```
SWEEP_RANGES: mode (7 modes), top_k (5/10/20), alpha (0.5–0.9), rrf_k (30/60/90), score_threshold (0/0.3/0.5), query_prefix (True/False).
Server URLs configurable via env: `EMBEDDING_URL`, `EMBEDDING_HEALTH_URL`, `SPLADE_URL`, `SPLADE_HEALTH_URL`, `RERANKER_URL`, `RERANKER_HEALTH_URL`.

**Output:** Per-query sections with doc/snippet/rank metrics + aggregate summary table + by-query-type breakdown. Sweep generates one per-config report + a comparison table across swept values.

**Baseline results (2026-05-24, CC α=0.8, top_k=12, query_prefix=True):**

| Collection | NDCG@12 | MRR@12 | Recall@12 | snippet_recall | doc_recall |
|---|---|---|---|---|---|
| test_db (2000/400, 250 chunks) | 0.691 | 0.735 | 83.3% | 83% | 100% |
| test_db_2 (1000/200, 511 chunks) | 0.653 | 0.698 | 75.5% | 75% | 100% |
| test_db_3 (512/100, 1027 chunks) | 0.547 | 0.593 | 67.2% | 67% | 100% |

## Evidenz

- **RAGAS (Evaluation Framework):** prescribes context_recall + context_precision as primary retrieval metrics; binary relevance via LLM-judge is valid for small GT sets. Ground truth at document-level (expected_documents) matches the RAGAS pattern. LLM-judge not needed here — relevance is by construction (see OldThemes below).
- **RAG Evaluation Survey 2025:** classifies retrieval metrics as document-level (MRR, MAP) vs chunk-level (Recall@K, NDCG@K). Distinguishes retrieval-only eval (our scope) from end-to-end RAG eval. NDCG@K is the most discriminative metric for ranked retrieval.
- **Pipeline Optimization Paper (arxiv:2511.22240):** uses Acc@3 and NDCG@3 on 11,000 synthetic QA pairs. Key finding: 512-char chunks outperform 2000-char by +5pp Acc@3. Provides reference point for benchmark scale; our 17-query GT is a minimal manual set.
- **Fusion Functions for Hybrid Retrieval (Bruch et al. 2023, ACM TOIS):** evaluates CC vs RRF fusion using NDCG@3 and NDCG@10. Direct methodological reference for using NDCG as the primary metric in fusion comparisons.
- **Methodology rationale + schema migration process:** `decisions/OldThemes/eval_suite/methodology_clarification_2026-05-24.md` (binary relevance by construction, why LLM-judge is not needed, why doc-level approximation is wrong) + `decisions/OldThemes/eval_suite/2026-05-24_phase_a_queries_sample.md` (Q1–Q3 sample: primary chunk identification, additional relevant chunk selection, cross-collection chunk_index lookup methodology).

## Recommendation (SOLL)

Baseline established (2026-05-24, see IST table). Next: `--sweep mode` on test_db to answer SPLADE question (dense vs hybrid vs cc) → IST update in `decisions/retrieval03_fusion.md`. Then `--sweep alpha` and `--sweep top_k`. Chunk-size sweep (test_db vs test_db_2 vs test_db_3 baseline comparison) already in IST — feed into `decisions/index01_chunking.md`.

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
