# Documentation Audit — 2026-05-11

## Summary

- **Files audited:** 28
- **Findings:** 25 (Critical: 10, Important: 12, Optional: 3)
- **Files clean:** DOCS.md (root), decisions/delivery01_mcp_tools.md, decisions/index04_storage.md, decisions/infra01_connection_management.md, decisions/retrieval01_query_embedding.md (structure OK, IST code path wrong → C4), all OldThemes/* (format OK)
- **Verification note:** `dev/cleanup/DOCS.md` could not be audited — directory does not exist (→ C10)

---

## Findings by Severity

### Critical (rule violations affecting current correctness)

#### C1: `server_manager.py` LOC 357 → 1061 in DOCS.md
- **File:** `src/rag/DOCS.md`
- **Section:** `### server_manager.py (357 LOC)`
- **Rule violated:** "LOC numbers must match actual `wc -l` output of the file"
- **Evidence:** `wc -l src/rag/server_manager.py` → 1061. Documented: 357. Drift: +704.
  Additionally, 1061 > 400 LOC hard ceiling — refactor-candidate flag is invisible until DOCS is corrected.
- **Recommended Fix:**
  ```
  Before: ### server_manager.py (357 LOC)
  After:  ### server_manager.py (1061 LOC)
  ```
  Also update the `Purpose:` line — the current description says "all three GPU servers" but SERVERS dict now has 5 presets (embedding-8b, embedding-0.6b, reranker-0.6b, reranker-8b, splade).

---

#### C2: Four undocumented modules in `src/rag/DOCS.md`
- **File:** `src/rag/DOCS.md`
- **Section:** `## Modules` (missing entries)
- **Rule violated:** "Module documentation on the level it lives on" — all modules in a multi-module directory must be documented
- **Evidence:** `ls src/rag/*.py` reveals these modules absent from DOCS.md:
  | Module | LOC | Callers (grep-verified) |
  |---|---|---|
  | `lock.py` | 132 | `cli.py`, `workflow.py` |
  | `status.py` | 169 | `cli.py`, `server_manager.py` (imports SERVERS, TIMESTAMP_DIR, status) |
  | `error_log.py` | 48 | `server_manager.py` (imports error_log.write) |
  | `server_lock.py` | 76 | no Python callers found — potential dead code, flag explicitly |
- **Recommended Fix:** Add four `### module.py (N LOC)` sections to `src/rag/DOCS.md` Modules block; flag `server_lock.py` as `Called by: [] (DEAD CODE — verify before removing)`.

---

#### C3: DOCS.md State table uses ghost path `~/.rag-locks/rag-server-{name}-last-used`
- **File:** `src/rag/DOCS.md`
- **Section:** `## State` (rows 169-170)
- **Rule violated:** "LOC numbers must match actual … Called-by must match actual grep results — not stale"; IST reflects production code
- **Evidence:**
  ```
  # DOCS.md claims:
  ~/.rag-locks/rag-server-{name}-last-used  → touch_timestamp via ensure_ready
  ~/.rag-locks/watchdog.pid                 → _ensure_watchdog_process
  ```
  ```python
  # server_manager.py actual:
  WATCHDOG_PID_FILE = Path.home() / ".rag-locks" / "watchdog.pid"  # ✓ correct
  # No touch_timestamp function; idle tracking via log file mtime:
  log = Path(state["log_path"])
  idle = now - log.stat().st_mtime   # _watchdog_tick line ~591
  # State files: TIMESTAMP_DIR / f"server-port-{port}.json"
  ```
  - `rag-server-{name}-last-used` file does not exist in current codebase
  - `touch_timestamp` function does not exist
  - Idle tracking is log-mtime-based, not timestamp-file-based
- **Recommended Fix:** Replace the stale `rag-server-{name}-last-used` row with the actual state:
  ```
  | ~/.rag-locks/server-port-{N}.json | Per-process state (pid, port, model, log_path, start_time); idle computed from log_path mtime | server_manager.py (watchdog_tick, purge_orphans) | server_manager.py (start — written after Popen; unlinked on stop) |
  ```

---

#### C4: `retrieval01_query_embedding.md` IST wrong code path for `embed_query()`
- **File:** `decisions/retrieval01_query_embedding.md`
- **Section:** `## Status Quo (IST)` line 5
- **Rule violated:** "IST reflects production code — not experiments, not plans, not 'what we want'"
- **Evidence:**
  ```
  # IST claims:
  Code: src/rag/retriever.py:embed_query()
  
  # Actual: search_primitives.py:13
  def embed_query(query: str) -> list[float]:
  # retriever.py:6 imports it:
  from .search_primitives import embed_query, search_vectors, bm25_search, splade_search
  ```
- **Recommended Fix:**
  ```
  Before: **Code:** `src/rag/retriever.py:embed_query()`
  After:  **Code:** `src/rag/search_primitives.py:embed_query()` (imported by `retriever.py`)
  ```

---

#### C5: `retrieval02_search.md` IST wrong code paths for all three search functions
- **File:** `decisions/retrieval02_search.md`
- **Section:** `## Status Quo (IST)` lines 5-7
- **Rule violated:** IST reflects production code
- **Evidence:**
  ```
  # IST claims:
  Code: src/rag/retriever.py:search_vectors(), splade_search(), bm25_search()
  
  # Actual: search_primitives.py
  def search_vectors(...)  → line 19
  def bm25_search(...)     → line 65
  def splade_search(...)   → line 133
  ```
  `retriever.py` imports all three: `from .search_primitives import embed_query, search_vectors, bm25_search, splade_search`
- **Recommended Fix:**
  ```
  Before: **Code:** `src/rag/retriever.py:search_vectors()`, `splade_search()`, `bm25_search()`
  After:  **Code:** `src/rag/search_primitives.py:search_vectors()`, `splade_search()`, `bm25_search()` (called via `retriever.py` imports)
  ```

---

#### C6: `retrieval04_reranking.md` IST says "Top 50 RRF candidates" but code uses CC fusion
- **File:** `decisions/retrieval04_reranking.md`
- **Section:** `## Status Quo (IST)`, line: `**Candidates:** Top 50 RRF candidates re-scored, top_k returned`
- **Rule violated:** IST reflects production code
- **Evidence:**
  ```python
  # retriever.py:99-100
  rrf_top = RERANK_CANDIDATES if rerank else top_k
  results = cc_fusion(vector_results, keyword_results, rrf_top)   # CC, not RRF
  ```
  `cc_fusion` is called unconditionally in `search_hybrid_workflow`. The variable `rrf_top` is a naming artifact — the fusion is CC. `rrf_fusion` is not called from the workflow (confirmed: grep finds no callsite other than fusion.py itself).
- **Recommended Fix:**
  ```
  Before: **Candidates:** Top 50 RRF candidates re-scored, top_k returned
  After:  **Candidates:** Top 50 CC-fused candidates (HYBRID_CANDIDATES=50 dense + 50 SPLADE via cc_fusion); top_k returned after rerank
  ```

---

#### C7: `eval01_methodology.md` IST uses stale test collection (RAG_MCP_test, 20 queries, 483 chunks)
- **File:** `decisions/eval01_methodology.md`
- **Section:** `## Status Quo (IST)` — multiple lines
- **Rule violated:** IST reflects production code (current state, not historical)
- **Evidence:**
  - IST says: `"Test collection: RAG_MCP_test — 20 queries, 483 chunks, mixed academic + technical docs."`
  - IST files list: `dev/retrieval/queries_rag_mcp_test.json — 20 hand-labeled queries`
  - Current state per `dev/retrieval/DOCS.md`: `queries_test_db.json` (17 queries, test_db collection, 250 chunks, 7 papers)
  - `queries_rag_mcp_test.json` is explicitly marked `"historical, retained for reference"` in dev/retrieval/DOCS.md
  - `RAG_MCP_test` collection was cleaned up 2026-04-30 (per `dev/retrieval/DOCS.md`)
  - Current test DB state: `rag_test`, collection `test_db`, 250 chunks (per `OldThemes/eval_suite/in_progress.md`)
- **Recommended Fix:** Update IST section:
  - Change test collection from `RAG_MCP_test` → `test_db`
  - Change query count from 20 → 17 and queries file from `queries_rag_mcp_test.json` → `queries_test_db.json`
  - Change chunk count from 483 → 250; corpus description from "mixed academic+technical" → "7 reference papers (RAG methodology)"

---

#### C8: `index03_sparse_embedding.md` Evidenz cites non-existent path
- **File:** `decisions/index03_sparse_embedding.md`
- **Section:** `## Evidenz`, `### Root Cause Analysis`
- **Rule violated:** Evidenz from sources only — path must be accurate
- **Evidence:**
  ```
  # IST claims:
  Root Cause Analysis (dev/retrieval_eval/analysis/splade_findings.md)
  
  # Actual dev/ structure:
  dev/retrieval/          (exists)
  dev/retrieval_eval/     (DOES NOT EXIST)
  ```
  `find dev/ -name "splade_findings.md"` → empty result.
- **Recommended Fix:** Either (a) update path to actual location if file was moved, or (b) replace the citation with a prose summary of the root cause analysis inline (the 4 bullet points that follow are sufficient — no link needed if the file doesn't exist). Remove the dead path reference.

---

#### C9: `CLAUDE.md` project tree missing four decision files
- **File:** `CLAUDE.md`
- **Section:** `## Project Structure` — `decisions/` subtree
- **Rule violated:** "CLAUDE.md — roughest project map, pipeline components, key files"
- **Evidence:**
  ```
  # CLAUDE.md lists in decisions/:
  index01_chunking.md, index02_dense_embedding.md, index03_sparse_embedding.md,
  index04_storage.md, retrieval01_query_embedding.md, retrieval02_search.md,
  retrieval03_fusion.md, retrieval04_reranking.md, delivery01_mcp_tools.md
  
  # On disk (not listed):
  box_architecture.md
  infra01_connection_management.md
  infra02_lock_and_status.md
  eval01_methodology.md
  OldThemes/ (entire subfolder not shown)
  ```
- **Recommended Fix:** Add the four missing files and OldThemes/ to the tree:
  ```
  ├── decisions/
  │   ├── box_architecture.md
  │   ├── eval01_methodology.md
  │   ├── index01_chunking.md ... (existing)
  │   ├── infra01_connection_management.md
  │   ├── infra02_lock_and_status.md
  │   └── OldThemes/              → process history (alternatives, superseded values)
  ```

---

#### C10: Ghost `dev/cleanup/` reference in CLAUDE.md and `dev/DOCS.md`
- **Files:** `CLAUDE.md` (Project Structure), `dev/DOCS.md` (Documentation Tree)
- **Rule violated:** Documentation Tree — "Only map the NEXT level of DOCS, not deeper levels"; CLAUDE.md accuracy
- **Evidence:**
  - `CLAUDE.md` line: `├── cleanup/                    → [DOCS.md](dev/cleanup/DOCS.md)`
  - `dev/DOCS.md` line: `- [cleanup/DOCS.md](cleanup/DOCS.md) — Web markdown cleanup scripts (per-collection)`
  - `ls dev/` → `DOCS.md  indexing  persisted_output_probe  retrieval` (no `cleanup/`)
  - Both the directory and its DOCS.md are missing
- **Recommended Fix:** Remove `cleanup/` entry from both CLAUDE.md and dev/DOCS.md.
  Additionally, add `dev/persisted_output_probe/` to dev/DOCS.md Documentation Tree (directory exists with `report.md`).

---

### Important (drift / consistency issues)

#### I1: `src/rag/DOCS.md` LOC drift — 8 modules with ≥5-line drift
- **File:** `src/rag/DOCS.md`
- **Rule violated:** "LOC numbers must match actual `wc -l` output"
- **Evidence:**
  | Module | Documented LOC | Actual LOC | Drift |
  |---|---|---|---|
  | `db.py` | 93 | 142 | +49 |
  | `formatting.py` | 38 | 59 | +21 |
  | `embedder.py` | 62 | 74 | +12 |
  | `sparse_embedder.py` | 47 | 58 | +11 |
  | `reranker.py` | 55 | 66 | +11 |
  | `sync.py` | 314 | 324 | +10 |
  | `retriever.py` | 145 | 151 | +6 |
  | `indexer.py` | 316 | 301 | -15 |
  (server_manager.py in C1; search_primitives.py 173/173 ✓, chunker.py 116/116 ✓, watchdog_main.py 7/7 ✓, splade_server.py 67/67 ✓, fusion.py 52/54 — 2-line drift below threshold)
- **Recommended Fix:** Update all 8 documented LOC values to match `wc -l`.

---

#### I2: `src/rag/DOCS.md` Called-by drift — 5 modules with missing callers
- **File:** `src/rag/DOCS.md`
- **Rule violated:** "Called-by must match actual grep results — not stale"
- **Evidence:**
  | Module | Documented Called-by | Missing Callers (grep-verified) |
  |---|---|---|
  | `db.py` | `retriever.py, search_primitives.py` | `indexer.py, sync.py, status.py, workflow.py` |
  | `chunker.py` | `workflow.py` | `sync.py` |
  | `indexer.py` | `workflow.py, sync.py` | `cli.py` (lazy import `from src.rag.indexer import delete_workflow`) |
  | `server_manager.py` | `embedder.py, sparse_embedder.py, reranker.py, workflow.py, watchdog_main.py` | `cli.py, sync.py, indexer.py, status.py` |
  | `sync.py` | `cli.py` | `workflow.py` |
- **Recommended Fix:** Update `Called by:` lines for all five modules.

---

#### I3: `sources/sources.md` format violates required table structure
- **File:** `sources/sources.md`
- **Rule violated:** `## sources/sources.md` → "Format: `| Source | Domain | Type | Decision Steps | Status |`"
- **Evidence:**
  Current format uses per-decision-step markdown sections (`## index01 — Chunking`) with subsections (`### Indexed`, `### Reddit`) and inline descriptions. Missing columns: Domain, Type, Status (`Referenced | Verified | Indexed (RAG: <collection>)`).
  
  Example gap — indexed entries say only "**Pipeline_Optimization** — arxiv 2511.22240" without `Indexed (RAG: RAG_reference)` status or Type (`Paper`).
- **Recommended Fix:** Migrate to single flat table:
  ```markdown
  | Source | Domain | Type | Decision Steps | Status |
  |---|---|---|---|---|
  | Pipeline_Optimization (arxiv:2511.22240) | RAG / Retrieval | Paper | index01, retrieval03, retrieval04, eval01 | Indexed (RAG: RAG_reference) |
  | ...
  ```

---

#### I4: `sources/sources.md` missing two indexed papers
- **File:** `sources/sources.md`
- **Rule violated:** sources.md tracks ALL external sources referenced or indexed
- **Evidence:**
  `rag-cli list_documents RAG_reference` confirms both are indexed:
  - `Score_Distribution_Calibration.md` (49 chunks) — arxiv 2105.04651, not in sources.md
  - `IR_Significance_Tests_Score_Distributions.md` (39 chunks) — arxiv 1901.10696, not in sources.md
  
  Per task spec: "Two papers were just added to RAG_reference: Score_Distribution_Calibration (arxiv 2105.04651) and IR_Significance_Tests_Score_Distributions (arxiv 1901.10696). Flag as missing-entries finding under eval01."
- **Recommended Fix:** Add both to sources.md under eval01 with `Indexed (RAG: RAG_reference)` status. Type: `Paper`.

---

#### I5: `infra02_lock_and_status.md` IST lock file table has stale server-related entries
- **File:** `decisions/infra02_lock_and_status.md`
- **Section:** `## Status Quo (IST)` — Lock files table
- **Rule violated:** IST reflects production code
- **Evidence:**
  ```
  # IST table claims:
  rag-server-<name>.last_used  | Per-GPU-server last-use timestamp
  rag-server-<name>.port       | Per-GPU-server port file
  
  # server_manager.py actual (confirmed via grep):
  # No rag-server-<name>.* files — current pattern is server-port-{N}.json
  # Idle tracking via log file mtime, not a last_used file
  ```
  These two rows describe the pre-dynamic-port implementation (documented in OldThemes/infra03_dynamic_ports.md as historical). The current implementation uses `server-port-{N}.json` JSON state files (per box_architecture.md IST).
- **Recommended Fix:** Remove the two stale rows. Replace with a cross-reference: `GPU server state (ports, PIDs, idle tracking) → see box_architecture.md IST.`

---

#### I6: `retrieval03_fusion.md` + `retrieval04_reranking.md` internal eval report in Quellen (should be in Evidenz) + missing script citation
- **Files:** `decisions/retrieval03_fusion.md`, `decisions/retrieval04_reranking.md`
- **Rule violated:** "Quellen: RAG Collection references, papers, URLs used as evidence. External sources only — internal eval reports belong in Evidenz, not here." AND "Internal eval results MUST cite: (a) the dev/ script, (b) the report-MD path, (c) the dataset."
- **Evidence:**
  Both files have in their `## Quellen` section:
  ```
  RAG_MCP Fusion Sweep (dev/retrieval/A_retrieval_eval_reports/sweep_comparison_20260408_190448.md)
  ```
  This is an internal report path → belongs in Evidenz.
  Additionally, neither file cites the dev/ script that produced the April 2026 sweep data (the eval harness predates `A_retrieval_eval.py` — it's an earlier version or unnamed script, but should be acknowledged or the fact that the harness is not reproducible should be noted).
- **Recommended Fix:**
  1. Move the `sweep_comparison_20260408_190448.md` citation from Quellen → Evidenz in both files.
  2. Add inline note: "Script: pre-A_retrieval_eval.py eval harness (not committed to repo — non-reproducible; data preserved in report)".
  3. Remove from Quellen.

---

#### I7: `retrieval03_fusion.md` + `retrieval04_reranking.md` stale RAG document names in Quellen
- **Files:** `decisions/retrieval03_fusion.md`, `decisions/retrieval04_reranking.md`
- **Rule violated:** "External evidence cites collection + document name from RAG"
- **Evidence:**
  - `retrieval03` Quellen: `"RAG Collection: Pipeline_Optimization_Paper"` → actual indexed name is `Pipeline_Optimization.md`
  - `retrieval04` Quellen: `"RAG Collection: Pipeline_Optimization_Paper"` → same
  - `retrieval04` Quellen: `"RAG Collection: Qwen3_Embedding_Paper"` → actual name `Qwen3_Embedding.md`
  - `retrieval04` Quellen: `"RAG Collection: qwen3reranker (model card details)"` → no such document/collection exists in RAG (confirmed: `rag-cli list_documents RAG_reference` shows no qwen3reranker entry)
- **Recommended Fix:**
  - `Pipeline_Optimization_Paper` → `Pipeline_Optimization`
  - `Qwen3_Embedding_Paper` → `Qwen3_Embedding`
  - Remove or replace `qwen3reranker` entry — if the model card was consulted, it was via the `Qwen3_Embedding.md` document (which covers the reranker architecture) or external URL.

---

#### I8: `index02_dense_embedding.md` Evidenz cites non-existent path `dev/indexing_benchmark/benchmark.py`
- **File:** `decisions/index02_dense_embedding.md`
- **Section:** `## Evidenz`, `### Server Config Benchmark`
- **Rule violated:** Evidenz paths must be accurate
- **Evidence:**
  ```
  # IST cites:
  Server Config Benchmark (dev/indexing_benchmark/benchmark.py)
  
  # Actual dev/ structure:
  dev/indexing/       (exists — no benchmark.py here)
  dev/indexing_benchmark/  (DOES NOT EXIST)
  ```
- **Recommended Fix:** Mark as "(historical benchmark, script no longer in repo)" inline. Remove the dead path or replace with the note that the data was collected once and the script was not committed.

---

#### I9: `index01_chunking.md` Evidenz cites non-existent `dev/indexing/chunking_eval/`
- **File:** `decisions/index01_chunking.md`
- **Section:** `## Evidenz`, `### Chunking Eval (dev/indexing/chunking_eval/)`
- **Rule violated:** Evidenz paths must be accurate
- **Evidence:**
  `ls dev/indexing/` → `A_chunking_stats_reports/, A_chunking_stats.py, A_index_collection_reports/, A_index_collection.py, DOCS.md, p1_chunker.py … p5_indexer.py` — no `chunking_eval/` subdir.
- **Recommended Fix:** Replace the path reference with the actual script that would perform this: `dev/indexing/A_chunking_stats.py`. Or mark as "(5-doc subset eval run ad-hoc, script not committed)".

---

#### I10: `dev/persisted_output_probe/` exists in dev/ but not in `dev/DOCS.md` Documentation Tree
- **File:** `dev/DOCS.md`
- **Rule violated:** Documentation Tree MUST include all direct subdirectories that have DOCS or scripts
- **Evidence:** `ls dev/` → `DOCS.md  indexing  persisted_output_probe  retrieval`. The directory contains `report.md` — a single-file probe. Per placement rules: single-module suites are documented in parent DOCS.md, not with own DOCS.md.
- **Recommended Fix:** Add a brief entry to `dev/DOCS.md`:
  ```markdown
  ### persisted_output_probe/
  Single-session probe for calibrating CLI persisted-output threshold. `report.md` — findings from 2026-05-10.
  ```

---

#### I11: `index02_dense_embedding.md` Evidenz missing report-MD path for MRL sweep
- **File:** `decisions/index02_dense_embedding.md`
- **Section:** `## Evidenz` — both MRL sweep tables
- **Rule violated:** "Internal eval results MUST cite script AND report-MD AND dataset"
- **Evidence:**
  - MRL Dimension Sweep (Qwen3_Embedding_Paper, 15 queries, 53 chunks): dataset OK, no dev/ script cited, no report-MD cited
  - MRL Dimension Sweep (searxng, 30 queries, 26088 chunks): dataset OK, no dev/ script cited, no report-MD cited
  - `dev/retrieval/A_mrl_sweep.py` exists and is the current sweep script, but may not have been the script used for these early sweeps (different timestamps / collections)
- **Recommended Fix:** Add: "Script: `dev/retrieval/A_mrl_sweep.py`. Report: `dev/retrieval/A_mrl_sweep_reports/<filename>.md` (if available — or mark non-reproducible if report was not committed)."

---

#### I12: `infra02_lock_and_status.md` SOLL section inconsistency — references scripts/idle_watchdog.py which may be superseded
- **File:** `decisions/infra02_lock_and_status.md`
- **Section:** `## Evidenz` Phase 2 description
- **Rule violated:** IST reflects production code
- **Evidence:**
  The Evidenz section mentions `scripts/idle_watchdog.py` + `scripts/install_watchdog.sh` in "Phase 2" description, and describes it as a LaunchAgent-based external idle watchdog. But `box_architecture.md` IST and `server_manager.py` both describe the watchdog as an **in-process detached subprocess** (`_ensure_watchdog_process`) — not a launchd LaunchAgent. The LaunchAgent approach is described in `infra03_dynamic_ports.md` (OldThemes) as the Phase 3/pre-server_manager approach. Infra02 Evidenz may be referencing a superseded architecture.
- **Recommended Fix:** Replace the Phase 2 idle-watchdog description in Evidenz with a pointer to the current in-process watchdog (`_ensure_watchdog_process` in `server_manager.py` / `box_architecture.md`).

---

### Optional (style / nice-to-haves)

#### O1: `index01_chunking.md` SOLL references chunk stats from deprecated collection
- **File:** `decisions/index01_chunking.md`
- **Section:** `## Recommendation (SOLL)`
- **Issue:** "Validated via A_chunking_stats: 483 chunks, avg 1736 chars, 80% in 1500-2000 bucket" — the 483-chunk collection is RAG_MCP (cleaned 2026-04-30). No A_chunking_stats report path cited. Stats still directionally valid for the KEEP decision.
- **Recommended Fix:** Add report path `(dev/indexing/A_chunking_stats_reports/…)` if the report is preserved; or update to reference the current collection stats if A_chunking_stats was re-run.

---

#### O2: `eval01_methodology.md` Offene Fragen reference n=20 queries throughout, should be n=17
- **File:** `decisions/eval01_methodology.md`
- **Section:** `## Offene Fragen`
- **Issue:** "Our 20 queries are insufficient…", "Train/dev/test split at n=20". Linked to C7 — once IST is updated to test_db (17 queries), these references become inconsistent.
- **Recommended Fix:** Update after C7 is applied — n=20 → n=17, `RAG_MCP_test` → `test_db` in all Offene Fragen references.

---

#### O3: `dev/DOCS.md` `dev/retrieval/DOCS.md` `A_retrieval_eval.py` default collection "RAG_MCP_test" superseded
- **File:** `dev/retrieval/DOCS.md`
- **Section:** CLI flags table, `--collection` flag
- **Issue:** Default `--collection RAG_MCP_test` is the deprecated collection. Active default should be `test_db`.
- **Recommended Fix:** Update CLI flags table default from `RAG_MCP_test` → `test_db`.

---

## Files Audited

| File | Status | Findings |
|---|---|---|
| `CLAUDE.md` | 2 findings | C9, C10 |
| `DOCS.md` (root) | Clean | — |
| `src/rag/DOCS.md` | 4 findings | C1, C2, C3, I1, I2 |
| `dev/DOCS.md` | 1 finding | C10 (ghost cleanup/), I10 |
| `dev/cleanup/DOCS.md` | **Cannot audit** — directory does not exist | C10 |
| `dev/indexing/DOCS.md` | Clean | — |
| `dev/retrieval/DOCS.md` | 1 finding | O3 |
| `sources/sources.md` | 2 findings | I3, I4 |
| `decisions/box_architecture.md` | Clean | — |
| `decisions/delivery01_mcp_tools.md` | Clean | — |
| `decisions/eval01_methodology.md` | 2 findings | C7, O2 |
| `decisions/index01_chunking.md` | 2 findings | I9, O1 |
| `decisions/index02_dense_embedding.md` | 2 findings | I8, I11 |
| `decisions/index03_sparse_embedding.md` | 1 finding | C8 |
| `decisions/index04_storage.md` | Clean | — |
| `decisions/infra01_connection_management.md` | Clean | — |
| `decisions/infra02_lock_and_status.md` | 2 findings | I5, I12 |
| `decisions/retrieval01_query_embedding.md` | 1 finding | C4 |
| `decisions/retrieval02_search.md` | 1 finding | C5 |
| `decisions/retrieval03_fusion.md` | 2 findings | I6, I7 |
| `decisions/retrieval04_reranking.md` | 4 findings | C6, I6, I7 |
| `decisions/OldThemes/connection_hang_cascade.md` | Clean | — |
| `decisions/OldThemes/infra03_dynamic_ports.md` | Clean (OldThemes historical context) | — |
| `decisions/OldThemes/null_embedding_qwen3_prefix.md` | Clean | — |
| `decisions/OldThemes/project_viz_layer.md` | Clean | — |
| `decisions/OldThemes/eval_suite/historical_setup_march2026.md` | Clean | — |
| `decisions/OldThemes/eval_suite/in_progress.md` | Clean | — |
| `decisions/OldThemes/eval_suite/process_2026-05-10.md` | Clean | — |

---

## IST vs Code Spot-Checks Performed

| Doku claim | Code reality | Verdict |
|---|---|---|
| `CC_ALPHA = 0.8` (retrieval03 IST) | `fusion.py:4` `CC_ALPHA = 0.8` | ✓ matches |
| `DENSE_SCORE_THRESHOLD = 0.01` (retrieval04 SOLL note) | `retriever.py:23` | ✓ matches |
| `HYBRID_CANDIDATES = 50` (retrieval02, retrieval04 IST) | `retriever.py:21` | ✓ matches |
| `rerank: bool = False` default (retrieval04 IST) | `retriever.py:90` `search_hybrid_workflow(…rerank: bool = False)` | ✓ matches |
| `DEFAULT_CHUNK_SIZE = 2000`, `DEFAULT_OVERLAP = 400` (index01 IST) | `chunker.py:14-15` | ✓ matches |
| `SPLADE_MODEL = "naver/splade-v3"` (index03 IST) | `splade_server.py:19` | ✓ matches |
| `max_active_dims=256` (index03 IST) | `splade_server.py:21,55` implied via sentence-transformers API | ✓ matches |
| `embed_query()` in `retriever.py` (retrieval01 IST) | `search_primitives.py:13` | ✗ DRIFT → C4 |
| `search_vectors()`, `bm25_search()`, `splade_search()` in `retriever.py` (retrieval02 IST) | `search_primitives.py:19,65,133` | ✗ DRIFT → C5 |
| CC fusion in search_hybrid (retrieval03 IST) | `retriever.py:100` `cc_fusion(…)` | ✓ matches |
| "Top 50 RRF candidates" (retrieval04 IST) | `retriever.py:100` `cc_fusion(…)` | ✗ DRIFT → C6 |
| `server_manager.py` LOC 357 (DOCS.md) | `wc -l` → 1061 | ✗ DRIFT → C1 |
| `top_k` clamped to 12 (retrieval04 SOLL / infra note) | `retriever.py:34,92,117` `min(top_k, 12)` | ✓ matches |
| CC min-max normalization formula (retrieval03 IST) | `fusion.py`: `(score - min_vec) / range_vec` for dense, `score / max_kw` for sparse | ✓ matches (per Code-Drift-Closure 2026-05-11 note) |

---

## Phase A Complete

Report at: `dev/docs_audit_2026-05-11.md`

**Findings summary:** 25 total — 10 Critical, 12 Important, 3 Optional.

**Top priorities by impact:**
1. **C2** — 4 undocumented modules (lock.py 132 LOC, status.py 169 LOC, error_log.py 48 LOC, server_lock.py 76 LOC — the latter likely dead code)
2. **C1** — server_manager.py 357 → 1061 LOC masks a >400-LOC hard-ceiling flag
3. **C3** — State table ghost path misleads any reader debugging server lifecycle
4. **C7** — eval01 IST points to deprecated collection, AI would query wrong eval setup
5. **C9** — CLAUDE.md tree missing 4 decision files means AI exploration skips them
