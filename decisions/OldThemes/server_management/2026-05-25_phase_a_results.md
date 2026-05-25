# Server Management — Phase A Results (2026-05-25)

Sister file to `2026-05-25_constellation_design.md` (design rationale + measurement plan). This file records what executing that plan produced.

---

## Smell-Test Results (6 Constellations)

Source: `dev/server_management/B_real_smell_reports/smell_20260525_182729.md`
Script: `dev/server_management/B_real_smell_test.py` (3 queries, top_k=12, rerank_candidates=12)

### VRAM Footprints

| Constellation | Servers | VRAM (GB) |
|---|---|---|
| C1 | embedding-8b | 9.01 |
| C2 | embedding-8b + splade | 9.01 |
| C3 | embedding-8b + reranker-0.6b | 15.93 |
| C4 | embedding-8b + reranker-8b | 23.87 |
| C5 | embedding-8b + splade + reranker-0.6b | 15.93 |
| C6 | embedding-8b + splade + reranker-8b | 23.87 |

All constellations fit in 48 GB unified memory (max C4/C6 at 23.87 GB). splade adds ~0 VRAM vs C3 (SPLADE is ~600 MB, dwarfed by other servers).

### Cold / Warm Latencies

| Constellation | Mode | Cold (ms) | Mean Warm (ms) |
|---|---|---|---|
| C1 | dense | 221 | 126 |
| C2 | hybrid | 382 | 194 |
| C2 | cc | 140 | 143 |
| C3 | dense+rerank-0.6b | 1807 | 1892 |
| C4 | dense+rerank-8b | 17666 | 19604 |
| C5 | cc+rerank-0.6b | 1971 | 2149 |
| C5 | hybrid+rerank-0.6b | 1909 | 2102 |
| C6 | cc+rerank-8b | 21728 | 22043 |
| C6 | hybrid+rerank-8b | 19402 | 21080 |

**Key finding: reranker-8b is unusably slow (~20s/query warm).** At 17–22s per query × 17 queries = 4.8–6.2 min per config, a 40-config sweep would take ~4 hours. Combined with the previous sweep's Watchdog-kill failures at that latency, reranker-8b is not viable on M4 Pro 48GB for batch eval sweeps, and is too slow for interactive production use. All `*+rerank-8b` modes dropped from prod consideration.

**reranker-0.6b smell-test discrepancy:** Warm latency in the smell test (rc=12) was ~1.9–2.1s, but the full sweep at rc=50 showed ~7s. Ratio matches: 12 candidates × ~160ms/pair ≈ 2s; 50 candidates × ~140ms/pair ≈ 7s. This is expected — rerank latency scales linearly with candidate count.

---

## Eval-Sweep Results (8 modes × 5 top_k = 40 configs)

Source: `dev/retrieval/A_retrieval_eval_reports/cross_mode_top_k_test_db_20260525_2028.md`
Log: `dev/retrieval/A_retrieval_eval_reports/cross_mode_top_k_test_db_20260525_2028.log`
Parameters: collection=test_db, 17 queries, alpha=0.8, rrf_k=60, rerank_candidates=50

### Primary: Snippet Recall % at top_k=12 (the decision-relevant slice)

| Mode | snippet_recall | NDCG | mean_lat |
|---|---|---|---|
| cc | 83% | 0.691 | 156ms |
| dense | 86% | 0.659 | 131ms |
| bm25 | 82% | 0.686 | 8ms |
| sparse | 85% | 0.695 | 36ms |
| hybrid | 80% | 0.708 | 157ms |
| cc+rerank | 97% | 0.665 | 7177ms |
| hybrid+rerank | 97% | 0.665 | 7026ms |
| dense+rerank-0.6b | 97% | 0.665 | 7448ms |

Full table (all top_k values): `cross_mode_top_k_test_db_20260525_2028.md`.

---

## Key Insights

### 1. Three rerank-0.6b modes converge identically at top_k=12

cc+rerank, hybrid+rerank, and dense+rerank-0.6b all produce snippet_recall=97% / NDCG=0.665 at top_k=12. The SPLADE server contributes zero measurable signal when the reranker is active — the reranker normalizes whatever the first-stage retriever returns to the same final ranking.

Implication: **dense+rerank-0.6b is the simplest viable rerank config.** No SPLADE server needed (saves 600 MB VRAM, reduces C5 to C3). For production, this is the cheapest constellation that achieves peak snippet recall.

### 2. Reranker cost: +17pp snippet recall at 45× latency

Non-rerank best (hybrid top_k=12): 80% snippet, 157ms  
Rerank best (any mode, top_k=12): 97% snippet, ~7100ms  
Trade-off: +17pp for 45× latency increase.

Whether this trade-off is acceptable depends on the downstream use case. For interactive MCP queries where the LLM synthesizes an answer from top-k chunks, the 7s latency per query means 7s added to each tool call — borderline for interactive use. For batch research, clearly acceptable.

### 3. Dense leads snippet recall without reranker; hybrid leads NDCG

At top_k=12 without reranker:
- Snippet recall leader: `dense` (86%) > `sparse` (85%) > `cc` (83%) > `bm25` (82%) > `hybrid` (80%)
- NDCG leader: `hybrid` (0.708) > `sparse` (0.695) > `cc` (0.691) > `bm25` (0.686) > `dense` (0.659)

The split is meaningful. Snippet recall measures whether the ground-truth chunk appears anywhere in the top-k set (binary hit). NDCG weights hits by rank — a relevant chunk at rank 1 scores much higher than one at rank 9. Hybrid's NDCG advantage means it tends to place the relevant chunk higher in the result list even when it retrieves fewer of them overall. For downstream LLM consumption where the model reads all k chunks, snippet recall (do we have the chunk at all?) may dominate. For direct answer extraction from the top result, NDCG (is the chunk near the top?) may dominate.

### 4. Reranker NDCG (0.665) is LOWER than hybrid no-rerank NDCG (0.708)

Despite reranking achieving 97% snippet recall vs hybrid's 80%, the reranked NDCG is lower. This happens because NDCG measures the full ranking — a reranker trained to push the best match to position 1 fills positions 2–12 with thematically-related but not query-specific chunks. The "tail" of a reranked result is noisier than a good first-stage ranking (hybrid), even though the top-1 position is better. For use cases where the LLM consumes only the top 2-3 chunks, reranked results are better. For use cases where the LLM reads all 12, hybrid is comparable or better.

### 5. Q7 and Q16 recovery (aggregate analysis only)

The sweep log contains per-query latency but not per-query snippet recall — cross-sweep stdout only reports aggregate summary stats per config.

Baseline cc top_k=12 snapshot (from `eval_baseline_20260524_234854.md`):
- Q7 ("How does RAGAS estimate faithfulness..."): 0/1 snippet (0%) — doc found at ranks 1–8, quote missing
- Q16 ("How do SPLADE-v3 and Rethinking Chunk Size each evaluate...": 1/2 snippets (50%) — missing "meta-analysis over more than 40 query sets"

At rc=50, the reranker receives 50 candidates. Quotes missing from top-12 can be recovered if they appear in candidates 13–50. The aggregate improvement from 83% (cc, top_k=12 baseline) to 97% (any rerank mode, top_k=12) = +14pp across 17 queries. Per-query recovery for Q7 and Q16 cannot be confirmed without re-running with full per-query logging, but both are mechanically viable recovery candidates.

---

## Infrastructure Work Landed in Phase A

All in `dev/` (eval tooling) and `src/rag/` (server management). Production code changes in `src/`:

- `server_utils.py`: `stop()` now reads PID from state-file before `kill -TERM`, removing race condition
- `server_utils.py`: `find_all_pids_on_port()` filters to `LISTEN` state only (was matching `ESTABLISHED` connections spuriously)
- `server_utils.py`: `_start_server_internal()` dynamic-port URL patching — `ensure_ready()` now patches `server_url` in config after binding to a dynamic port, so clients get the correct URL
- `p1_retriever.py` (dev): `--restrict-modes` flag added for fast single-mode smoke testing
- `eval_config.py` (dev): `rerank_candidates` promoted to first-class sweep parameter
- `A_retrieval_eval.py`: `_rerank_at()` timeout extended 60s → 300s
- `A_retrieval_eval.py`: latency tracking added to cross-sweep (6th tuple element)
- `A_retrieval_eval.py`: `_write_cross_sweep_report()` fixed to unpack 6-element tuple (this session, A2)

---

## Open: rerank_candidates dimension not measured

All rerank configs in Phase A used `rerank_candidates=50`. The latency-vs-recall trade-off for the reranker has not been characterized. Hypothesis: lower rc values reduce latency proportionally (linear candidate count) at some snippet recall cost. Next dimension to sweep (Phase B):

- Modes: the three rerank-0.6b modes at top_k=12 (or only dense+rerank-0.6b since they're equivalent)
- rerank_candidates values: 20, 30, 40 (below the current rc=50 baseline)
- Expected data: does rc=20 still hit 90%+ snippet recall at ~3s/query?

---

## Open: chunk-size matrix on test_db_2 / test_db_3 not run

Deferred. Waiting for prod-config (mode + top_k + rerank_candidates) to finalize in Phase B before running the chunk-size comparison across datasets.
