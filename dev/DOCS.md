# dev/ — Development & Evaluation Scripts

Pipeline-oriented layout matching the RAG system architecture. Scripts for evaluating, profiling, and validating the indexing and retrieval pipelines.

All scripts run from project root with the project venv:

```bash
./venv/bin/python dev/<path>/<script>.py [args]
```

Scripts that access the database import from `src.rag` and expect PostgreSQL on port 5433.

## Test Database

Dev scripts that write to PostgreSQL use `rag_test` (never `rag` prod DB).

```bash
# One-time setup
bash dev/indexing/chunking_eval/setup_test_db.sh

# Use via env var
POSTGRES_DB=rag_test ./venv/bin/python dev/indexing/splade_truncation/reproduce.py ...
```

Schema is identical to prod — created by `src/rag/indexer.py:ensure_schema()` on first use.

Used by: `chunking_eval/`, `splade_truncation/`

## Documentation Tree

- [cleanup/DOCS.md](cleanup/DOCS.md) — Web markdown cleanup scripts (per-collection)
- [indexing/DOCS.md](indexing/DOCS.md) — Indexing pipeline evaluation (chunking, embedding, DB profiling)
- [retrieval/DOCS.md](retrieval/DOCS.md) — Retrieval pipeline evaluation (reranker validation, quality metrics)
