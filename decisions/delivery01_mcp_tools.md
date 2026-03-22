# Delivery (MCP Tools)

## Status Quo (IST)

- FastMCP server started via `mcp-start.sh` (PostgreSQL + FastMCP, no GPU)
- 6 MCP tools exposed in `server.py`:
  - `search` — dense-only search with optional reranking
  - `search_hybrid` — dense + sparse fusion (RRF) with optional reranking
  - `search_keyword` — sparse-only (SPLADE) search
  - `list_collections` — list indexed collections
  - `list_documents` — list documents in a collection
  - `read_document` — read document chunks sequentially
- list/read tools work without GPU servers
- search tools require GPU servers (auto-started on demand by `server_manager.py`)

## Evidenz

No benchmarks run. Tool interface designed for Claude Code consumption.

## Recommendation (SOLL)

Pending — needs evaluation.

## Offene Fragen

- Are the current tool signatures optimal for Claude Code usage patterns?
- Should `search` and `search_hybrid` be merged into one tool with a `mode` parameter?

## Quellen

None yet.
