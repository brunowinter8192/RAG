# dev/ — Development & Evaluation Scripts

Pipeline-oriented layout matching the RAG system architecture. Scripts for evaluating, profiling, and validating the indexing and retrieval pipelines.

All scripts run from project root with the project venv:

```bash
./venv/bin/python dev/<path>/<script>.py [args]
```

Scripts that access the database import from `src.rag` and expect PostgreSQL on port 5433.

## Documentation Tree

- [cleanup/DOCS.md](cleanup/DOCS.md) — Web markdown cleanup scripts (per-collection)
- [indexing/DOCS.md](indexing/DOCS.md) — Indexing pipeline evaluation (chunking, embedding, DB profiling)
- [retrieval/DOCS.md](retrieval/DOCS.md) — Retrieval pipeline evaluation (reranker validation, quality metrics)
