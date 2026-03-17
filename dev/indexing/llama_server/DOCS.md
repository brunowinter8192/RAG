# dev/indexing/llama_server/ — Reranker Server Debugging

Debug scripts for investigating llama-server reranker issues (500 errors, batch size limits). Created to diagnose the reranker 500 error (ccf86f2). Root cause: llama-server needed `-ub`/`-b 4096` batch size flags for the reranker model.

---

## 01_capture_stderr.py

**Purpose:** Start the reranker server (0.6B, port 8082) with stderr/stdout captured to log files. Useful for seeing llama.cpp internal errors that are otherwise hidden.
**Input:** None (no arguments).
**Output:** Log files in `01_server_logs/stderr_*.log` and `stdout_*.log`.

**Usage:**
```bash
./venv/bin/python dev/indexing/llama_server/01_capture_stderr.py
```

---

## 02_reproduce_500.py

**Purpose:** Stress test the reranker with varying chunk counts to reproduce 500 errors. Supports multiple test modes.
**Input:** Optional mode flag (`--synthetic`, `--verify`, `--compare`). Default uses real DB chunks.
**Output:** Response logs in `02_responses/run_*.json`.

**Modes:**

| Flag | Description |
|------|-------------|
| (default) | Real DB chunks, tests chunk counts 5–20 |
| `--synthetic` | Synthetic chunks, tests counts 5–50 |
| `--verify` | Sanity check with known-answer test (bread recipe, Issue #16407 data) |
| `--compare` | Compare two models on same data (port 8082 vs 8083) |

**Usage:**
```bash
./venv/bin/python dev/indexing/llama_server/02_reproduce_500.py
./venv/bin/python dev/indexing/llama_server/02_reproduce_500.py --synthetic
./venv/bin/python dev/indexing/llama_server/02_reproduce_500.py --verify
./venv/bin/python dev/indexing/llama_server/02_reproduce_500.py --compare
```

---

## 03_test_batch_size.py

**Purpose:** Test the reranker server with different `-b` (batch size) flags: 512, 1024, 2048, 4096. Restarts server for each batch size to identify which value avoids 500 errors.
**Input:** None (no arguments).
**Output:** Per-batch-size test results to stdout.

**Usage:**
```bash
./venv/bin/python dev/indexing/llama_server/03_test_batch_size.py
```
