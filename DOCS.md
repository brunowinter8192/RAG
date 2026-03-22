# RAG MCP Server — Root Modules

## Documentation Tree

- [src/DOCS.md](src/DOCS.md) — Source code packages (RAG pipeline modules, spawn utilities)
- [dev/DOCS.md](dev/DOCS.md) — Development & evaluation scripts

---

## server.py

**Purpose:** FastMCP server exposing RAG retrieval as MCP tools. Entry point for the MCP server process.
**Input:** MCP tool calls from Claude Code (query, collection, filters, options).
**Output:** `list[TextContent]` — formatted search results or document content.

Tools registered:

| Tool | Description |
|------|-------------|
| `search` | Dense vector search (cosine similarity) |
| `search_hybrid` | Dense + SPLADE sparse search with RRF fusion and optional reranking |
| `search_keyword` | BM25 full-text keyword search |
| `list_collections` | List all indexed collections with chunk counts |
| `list_documents` | List all documents in a collection |
| `read_document` | Read continuous text from a document at a specific chunk offset |

**Usage:**
```bash
# Started automatically by mcp-start.sh
fastmcp run server.py
```

---

## workflow.py

**Purpose:** CLI for pipeline operations — chunking, indexing, search, SPLADE backfill, and GPU server management. Human-triggered, not MCP.
**Input:** CLI arguments (subcommands below).
**Output:** Stdout — progress messages, search results, server status, or deletion counts.

**Subcommands:**

| Command | Description |
|---------|-------------|
| `index-json` | Index chunks from a pre-chunked `chunks.json` file |
| `search` | Run a dense search query and print results |
| `chunk` | Chunk a markdown file and write a `chunks.json` |
| `backfill-splade` | Fill NULL sparse embeddings for an existing collection |
| `delete` | Delete chunks by collection and/or document |
| `server` | Manage GPU servers — status, start, stop, restart |

**Usage:**
```bash
./venv/bin/python workflow.py index-json --input data/documents/MyCollection/chunks.json
./venv/bin/python workflow.py search --query "hybrid retrieval" --collection RAG_MCP --top-k 5
./venv/bin/python workflow.py chunk --input data/documents/MyCollection/doc.md --chunk-size 1000
./venv/bin/python workflow.py backfill-splade --collection RAG_MCP
./venv/bin/python workflow.py delete --collection MyCollection
./venv/bin/python workflow.py server status
./venv/bin/python workflow.py server start
./venv/bin/python workflow.py server stop
./venv/bin/python workflow.py server restart splade
```

---

## start.sh

**Purpose:** Start PostgreSQL and all GPU servers via `workflow.py server start`.
**Input:** None (no arguments). Requires GGUF model files under `models/`.
**Output:** Running PostgreSQL + all GPU servers (embedding, reranker, SPLADE).

**Usage:**
```bash
./start.sh
```

---

## mcp-start.sh

**Purpose:** Start the MCP server with minimal dependencies — no GPU servers required for `list_*` and `read_document`.
**Input:** None (no arguments). Bootstraps venv if missing.
**Output:** Running FastMCP server process (executes `fastmcp run server.py`).

Behavior:
- Creates and installs venv from `requirements.txt` if not present
- Starts PostgreSQL if not already running (checks port 5433)
- GPU servers auto-start on demand when search/index operations are called (via `server_manager.ensure_ready()`)
- GPU servers auto-stop after 5 minutes idle (configurable via `RAG_SERVER_IDLE_TIMEOUT` env var)

**Usage:**
```bash
./mcp-start.sh
# Or configured as MCP server command in Claude Code settings
```
