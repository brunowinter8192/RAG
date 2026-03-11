# Worker Report: reranker-8b

## Task
Create a validation test script for the 8B reranker model to detect defective GGUF builds (mradermacher Issue #16407 — produces 0.0 scores).

## Results
Two files created in `dev/reranker_8b/`:

- `test_8b_reranker.py`: Starts 8B server on port 8084, sends two test queries with 3 docs each (relevant/somewhat_relevant/irrelevant), prints comparison table vs 0.6B on port 8082, validates scores are non-zero and ranking is correct, then shuts down the 8B server.
- `README.md`: Documents what the test validates, how to run it, how to interpret results, and what to do if 8B fails.

Script computes `RAG_ROOT` from `__file__` so paths work from any working directory.

## Files Changed
- `dev/reranker_8b/test_8b_reranker.py` — validation test script (new)
- `dev/reranker_8b/README.md` — documentation (new)
- `WORKER_REPORT.md` — this report (new)

## Open Issues
None. Script is ready to run. 0.6B server must be running on port 8082 before execution (it is assumed to already be running as production server).
