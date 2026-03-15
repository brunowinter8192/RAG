# dev/ — Development & Debugging Scripts

Standalone scripts for testing, debugging, and data preparation. Exempt from CLAUDE.md compliance.

## Directories

| Directory | Purpose | Key Scripts |
|-----------|---------|-------------|
| `cleanup/` | SearXNG Sphinx docs cleaning (v2, production) | `clean_web_SearXNG_Docs.py` |
| `explore/` | Pattern analysis & initial cleaning (v1, predecessor to cleanup/) | `analyze_patterns.py`, `clean_searxng.py` |
| `llama_server/` | llama-server debugging (reranker 500 errors, batch size tuning) | `01_capture_stderr.py`, `02_reproduce_500.py`, `03_test_batch_size.py` |
| `splade_benchmark/` | Sequential vs parallel embedding benchmark (dense + SPLADE) | `benchmark.py` |
| `reranker_8b/` | Reranker 8B GGUF validation (mradermacher defect detection) | `test_8b_reranker.py` |
| `indexing_benchmark/` | Indexing pipeline profiling (dense, sparse, DB timing per batch) | `benchmark.py` |
| `retrieval_eval/` | Retrieval quality evaluation (BEIR-format, pytrec_eval metrics) | `eval_runner.py` |

## Usage

All scripts run from project root with the project venv:

```bash
./venv/bin/python dev/<directory>/<script>.py [args]
```

Scripts that access the database import from `src.rag` and expect PostgreSQL on port 5433.
