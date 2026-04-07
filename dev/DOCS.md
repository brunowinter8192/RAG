# dev/ — Development & Evaluation Scripts

Pipeline-oriented layout matching the RAG system architecture. Scripts for evaluating, profiling, and validating the indexing and retrieval pipelines.

All scripts run from project root with the project venv:

```bash
./venv/bin/python dev/<path>/<script>.py [args]
```

## Test Database

Dev scripts that write to PostgreSQL use `rag_test` (never `rag` prod DB).

```bash
# One-time setup
docker exec rag-postgres psql -U rag -d postgres -c "CREATE DATABASE rag_test;"
```

Schema is created automatically by `p4_db.py:ensure_schema()` on first use.

## Documentation Tree

- [cleanup/DOCS.md](cleanup/DOCS.md) — Web markdown cleanup scripts (per-collection)
- [indexing/DOCS.md](indexing/DOCS.md) — Indexing pipeline modules and scripts
- [retrieval/DOCS.md](retrieval/DOCS.md) — Retrieval pipeline modules and scripts
