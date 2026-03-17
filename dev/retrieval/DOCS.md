# dev/retrieval/ — Retrieval Pipeline Evaluation

Scripts for evaluating and validating the retrieval pipeline (reranker models, retrieval quality).

## Documentation Tree

- [eval/DOCS.md](eval/DOCS.md) — BEIR-format retrieval evaluation suite (pytrec_eval)

---

## reranker_8b/test_8b_reranker.py

**Purpose:** Validate that `Qwen3-Reranker-8B-Q8_0.gguf` produces sane relevance scores. Background: mradermacher GGUF conversions of Qwen3-Reranker are known defective (Issue #16407) and produce 0.0 scores for all documents.
**Input:** None (no arguments). Starts the 8B server on port 8084 and uses the running 0.6B production server on port 8082 for comparison.
**Output:** Side-by-side score table and validation result (PASS/FAIL) to stdout.

**Validation checks:**
1. Scores are not all 0.0 (defective model indicator)
2. `score(relevant) > score(irrelevant)` for each test case
3. Scores in `[0.0, 1.0]` range (warning if outside)

**Prerequisites:**
- 0.6B reranker server running on port 8082 (production server — do not stop it)
- `httpx` installed in venv
- `models/Qwen3-Reranker-8B-Q8_0.gguf` present

**Interpretation:**
- `RESULT: 8B model produces valid scores` — model is good, safe to use in production
- `RESULT: 8B model validation FAILED` — model is defective (likely mradermacher source); keep using 0.6B

**Usage:**
```bash
./venv/bin/python dev/retrieval/reranker_8b/test_8b_reranker.py
```
