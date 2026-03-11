# Reranker 8B Validation

Validates that `Qwen3-Reranker-8B.Q8_0.gguf` produces sane relevance scores.

Background: mradermacher GGUF conversions of Qwen3-Reranker are known defective (Issue #16407) and produce 0.0 scores for all documents.

## What the test checks

1. Scores are not all 0.0 (defective model indicator)
2. Relevant documents score higher than irrelevant documents
3. Side-by-side comparison with the known-working 0.6B model

## Prerequisites

- 0.6B reranker server running on port 8082 (production server, do not stop it)
- `httpx` installed in the venv

## How to run

```bash
./venv/bin/python dev/reranker_8b/test_8b_reranker.py
```

The script starts the 8B server on port 8084, runs tests, then shuts it down.

## How to interpret results

**RESULT: 8B model produces valid scores** — model is good, safe to use in production.

**RESULT: 8B model validation FAILED** — model is defective (likely mradermacher source).

Validation criteria:
- At least one score != 0.0
- For each test case: `score(relevant) > score(irrelevant)`

## If 8B fails

Keep using `models/qwen3-reranker-0.6b-q8_0.gguf` on port 8082. Download 8B from a
different source (official Qwen HuggingFace repo, not mradermacher).
