# Retrieval Step 4: Reranking

## Status Quo (IST)

**Code:** `search_hybrid_workflow()` in `src/rag/retriever.py`
**Model:** Qwen3-Reranker-0.6B Q8_0 via llama-server
**Server:** llama-server on port 8082, `--rerank -c 32768 -np 1`
**top_k:** Hardcoded 12 (no parameter). `search_hybrid_workflow()` signature no longer accepts `top_k`.

### Two code paths based on `rerank` parameter

**`rerank=True` (dense+rerank path):**
- First stage: `search_vectors()` fetches `RERANK_CANDIDATES=30` dense candidates
- No `splade_search()` call, no `cc_fusion()` call
- Constellation: embedding-8b + reranker-0.6b (C3, 15.93 GB VRAM — no SPLADE server needed)
- `rerank_workflow()` re-scores all 30 candidates, returns top 12; score == 0 excluded

**`rerank=False` (cc-fusion path, default):**
- First stage: `search_vectors()` + `splade_search()`, each fetching `HYBRID_CANDIDATES=50` candidates
- `cc_fusion()` merges and returns top 12
- Constellation: embedding-8b + splade (C2, 9.01 GB VRAM)

**Constants** (`src/rag/retriever.py`):
- `RERANK_CANDIDATES = 30` (Phase B plateau: rc=30 hits 97% snippet recall, identical to rc=50 at 37% lower latency)
- `HYBRID_CANDIDATES = 50`
- DEFAULT_TOP_K removed (top_k hardcoded 12 in workflow body)

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

Reranker adds +4pp Doc Recall but costs -1pp Snippet Recall. CC+Rerank = Hybrid+Rerank (reranker normalizes fusion method). For MCP tool responses where snippet quality matters more than document discovery, reranking is not recommended on technical-doc collections.

Script: pre-A_retrieval_eval.py eval harness (not committed to repo — non-reproducible; data preserved in report).
Report: `dev/retrieval/A_retrieval_eval_reports/sweep_comparison_20260408_190448.md`

### Cross-Mode + top_k Sweep (test_db, 8 modes × 5 top_k, 2026-05-25)

Script: `dev/retrieval/A_retrieval_eval.py --sweep-cross mode top_k --collection test_db`
Report: `dev/retrieval/A_retrieval_eval_reports/cross_mode_top_k_test_db_20260525_2028.md`
Dataset: test_db (250 chunks, 7 academic papers, 17 queries, rerank_candidates=50)

| Mode | snippet_recall @top_k=12 | NDCG | mean_lat |
|---|---|---|---|
| hybrid | 80% | **0.708** | 157ms |
| dense | **86%** | 0.659 | 131ms |
| cc+rerank | **97%** | 0.665 | 7177ms |
| hybrid+rerank | **97%** | 0.665 | 7026ms |
| dense+rerank-0.6b | **97%** | 0.665 | 7448ms |

Key findings:
- All three rerank-0.6b modes converge to identical results at top_k=12 → SPLADE adds zero signal when reranker is active
- Reranker NDCG (0.665) is lower than hybrid no-rerank (0.708): reranker hoists best chunk to rank 1 but fills tail with thematically-related but off-target chunks; cc-fusion maintains better overall ranking
- Reranker buys +17pp snippet recall (80%→97%) at 45× latency cost (157ms→7200ms)
- dense+rerank-0.6b is the simplest rerank constellation (C3: embedding-8b + reranker-0.6b, no SPLADE)

### rerank_candidates Sweep — plateau at rc=30 (test_db, 2026-05-25)

Script: `dev/retrieval/A_retrieval_eval.py --sweep rerank_candidates --override mode=dense+rerank-0.6b`
Report: `dev/retrieval/A_retrieval_eval_reports/cross_mode_rerank_candidates_test_db_20260525_211134.md`

| rc | snippet_recall | mean_lat |
|---|---|---|
| 20 | 94% | 2828ms |
| **30** | **97%** | **4539ms** |
| 40 | 97% | 6276ms |
| 50 | 97% | 7228ms |

Plateau at rc=30: all rc ≥ 30 produce identical 97% recall. rc=30 is 37% faster than rc=50.
Up-sweep (rc=60–80) produced identical results to rc=50 due to `CANDIDATES=50` cap in `dev/retrieval/p1_retriever.py:19` — genuine rc>50 not measured. The 97% ceiling is not rc-limited.

### Quote Coverage Audit — 97% ceiling is structural, not tunable

Script: `dev/chunker/A_quote_coverage.py`
Report: `dev/chunker/A_quote_coverage_reports/coverage_20260525_230358.md`

All 28 identifying_quotes in queries_test_db.json are present verbatim in single chunks (100% single-chunk match, 0 boundary splits, 0 missing). The 3% gap is not a chunking or index problem.

**Q16 known limit:** The persistent missing snippet at all rc values is Q16 quote 2 — `"recall @ k trends for different chunk sizes and embedding models"` from `Rethinking_Chunk_Size_Long_Document.md` chunk 3. Chunk 3 is a dataset statistics table; its dense embedding is dominated by table data (NarrativeQA, NQ, etc.) and sits far from the Q16 query embedding, which is pulled toward SPLADE-v3 content by the explicit "SPLADE-v3" mention. This is a semantic-asymmetry failure on a cross-document query, not a retrieval-system defect. Raising `CANDIDATES` or `rc` will not recover this snippet.

97% snippet recall on test_db is the verified ceiling for this query set with the current chunking strategy.

## Recommendation (SOLL)

- **Keep:** `rerank=False` as default — for technical-doc collections (code, API refs, configs, monitoring logs) reranker hurts NDCG and adds 45× latency. Use `--rerank` only for academic/prose collections.
- **Keep:** `RERANK_CANDIDATES=30` — plateau confirmed on test_db, 37% latency saving vs rc=50 at identical recall.
- **Keep:** dense-only first stage for `rerank=True` path (no SPLADE) — SPLADE adds zero signal when reranker is active; simpler constellation (C3 vs C5), saves 600 MB VRAM.
- **Keep:** Qwen3-Reranker-0.6B model — 97% snippet recall on academic text, ~4.5s/query at rc=30.
- **Usage guidance — domain dependency:**
  - Academic / prose collections (papers, wiki, documentation): `--rerank` appropriate. +17pp snippet recall, ~4.5s/query.
  - Technical collections (code, configs, API references, monitoring): omit `--rerank`. CC-fusion at 131–157ms/query, NDCG superior (0.708 vs 0.665).
- **Resolved:** reranker-8b eliminated — ~20s/query warm latency on M4 Pro 48GB (C4/C6 smell test), unusable for interactive and batch.

### CLI Default + Threshold Changes 2026-05-11

**CLI default flip (commit `f6fecc8`):** `cli.py` `search_hybrid` flag changed from `--no-rerank` (default=True) to `--rerank` (default=False). CLI default now matches `search_hybrid_workflow(rerank: bool = False)` function signature and the SOLL statement "Keep rerank=False as default". Previous CLI-vs-Decision inconsistency resolved.

**Post-rerank score threshold removed (commit `1d80fd4`):** Hard 0.3 threshold eliminated. `rerank_workflow` internal `[:top_k]` handles candidate selection; only exact score == 0 excluded via inline list comprehension. Threshold calibration Pending item removed — no longer applicable for the rerank path.

## Offene Fragen

- ~~What is the actual NDCG improvement on our data?~~ **RESOLVED:** -8.5pp NDCG on RAG_MCP (technical/mixed); +17pp snippet recall on test_db (academic). Domain-dependent.
- ~~Latency: How much time does reranking add per query?~~ **RESOLVED:** ~4.5s/query (rc=30, reranker-0.6b, warm). 45× overhead vs cc-fusion (157ms).
- Is 0.6B sufficient or would 4B/8B reranker improve quality? Reranker-8b measured at ~20s/query — eliminated. No further 8B eval planned.
- ColBERT reranking (late interaction) as alternative? VectorChord blog shows ColBERT + pgvector integration with +30% NDCG@10.

## Quellen

- RAG Collection: Pipeline_Optimization (reranking benefits: +9.4pp Acc@3)
- RAG Collection: Qwen3_Embedding (Qwen3-Reranker architecture and benchmarks)
- ColBERT + pgvector blog (VectorChord — MaxSim in PostgreSQL)
- Bruch et al. 2023 "An Analysis of Fusion Functions for Hybrid Retrieval" (ACM TOIS, arXiv:2210.11934)
