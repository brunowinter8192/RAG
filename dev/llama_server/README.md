# llama_server/ — Reranker Server Debugging

Debug scripts for investigating llama-server reranker issues (500 errors, batch size limits).

## Scripts

**`01_capture_stderr.py`** — Starts reranker server (0.6B, port 8082) with stderr/stdout capture to log files. Useful for seeing llama.cpp internal errors.

```bash
./venv/bin/python dev/llama_server/01_capture_stderr.py
# Logs -> 01_server_logs/stderr_*.log, stdout_*.log
```

**`02_reproduce_500.py`** — Stress tests the reranker with varying chunk counts. Multiple modes:
- Default (db): Uses real DB chunks, tests counts 5-20
- `--synthetic`: Synthetic chunks, tests counts 5-50
- `--verify`: Sanity check with known-answer test (bread recipe, Issue #16407 test data)
- `--compare`: Compares two models on same data (port 8082 vs 8083)

```bash
./venv/bin/python dev/llama_server/02_reproduce_500.py [--synthetic|--verify|--compare]
# Results -> 02_responses/run_*.json
```

**`03_test_batch_size.py`** — Tests reranker with different `-b` (batch size) flags: 512, 1024, 2048, 4096. Restarts server for each size. Identifies which batch size avoids 500 errors.

```bash
./venv/bin/python dev/llama_server/03_test_batch_size.py
```

## Context

These scripts were created to debug the reranker 500 error (ccf86f2). Root cause: llama-server needed `-ub`/`-b 4096` batch size flags for the reranker model.
