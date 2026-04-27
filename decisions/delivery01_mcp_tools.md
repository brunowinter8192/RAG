# Delivery (CLI Tools via agent-rag-search Skill)

## Status Quo (IST)

- RAG retrieval tools exposed as CLI subcommands in `cli.py`, wrapped by `rag-cli` at `~/.local/bin/rag-cli` (in PATH)
- Consumed by Claude Code via the `agent-rag-search` Skill (`skills/agent-rag-search/SKILL.md`)
- PostgreSQL required for all operations; GPU servers auto-started on demand by `server_manager.py`
- `list_collections`, `list_documents`, `read_document` work without GPU servers; search subcommands require GPU servers
- Direct CLI integration — no server process required for session start
| Subcommand | Description |
|---|---|
| `search` | Dense vector search (cosine similarity) |
| `search_hybrid` | Dense + SPLADE + CC fusion; optional cross-encoder reranking |
| `search_keyword` | BM25 full-text keyword search |
| `list_collections` | List indexed collections with chunk counts |
| `list_documents` | List documents in a collection |
| `read_document` | Read document chunks sequentially |

## Evidenz

No benchmarks run. Tool interface designed for Claude Code consumption via Skill.

## Recommendation (SOLL)

Pending — needs evaluation.

## Offene Fragen

- Are the current tool signatures optimal for Claude Code usage patterns?
- Should `search` and `search_hybrid` be merged into one tool with a `mode` parameter?

## Quellen

None yet.
