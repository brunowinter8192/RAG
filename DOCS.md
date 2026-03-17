# RAG MCP Server — Root Modules

## Documentation Tree

- [src/rag/DOCS.md](src/rag/DOCS.md) — Pipeline modules (chunking, embedding, indexing, retrieval)
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

**Purpose:** CLI for pipeline operations — chunking, indexing, search, and SPLADE backfill. Human-triggered, not MCP.
**Input:** CLI arguments (`index-json`, `search`, `chunk`, `backfill-splade`, `delete` subcommands).
**Output:** Stdout — progress messages, search results, or deletion counts.

**Subcommands:**

| Command | Description |
|---------|-------------|
| `index-json` | Index chunks from a pre-chunked `chunks.json` file |
| `search` | Run a dense search query and print results |
| `chunk` | Chunk a markdown file and write a `chunks.json` |
| `backfill-splade` | Fill NULL sparse embeddings for an existing collection |
| `delete` | Delete chunks by collection and/or document |

**Usage:**
```bash
./venv/bin/python workflow.py index-json --input data/documents/MyCollection/chunks.json
./venv/bin/python workflow.py search --query "hybrid retrieval" --collection RAG_MCP --top-k 5
./venv/bin/python workflow.py chunk --input data/documents/MyCollection/doc.md --chunk-size 1000
./venv/bin/python workflow.py backfill-splade --collection RAG_MCP
./venv/bin/python workflow.py delete --collection MyCollection
```

---

## start.sh

**Purpose:** Start all GPU inference servers (embedding + SPLADE) and PostgreSQL for full indexing/retrieval.
**Input:** None (no arguments). Requires GGUF model files under `models/`.
**Output:** Running servers on ports 8081 (dense embedding), 8082 (reranker, commented out), 8083 (SPLADE via `scripts/start_splade_server.sh`).

Starts:
1. PostgreSQL via `docker compose up -d postgres`
2. `llama-server` for dense embeddings (Qwen3-Embedding-8B-Q8_0, port 8081, Metal GPU)

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
- Exports `POSTGRES_PORT` env var
- Does NOT start embedding or SPLADE servers (those fail gracefully if absent)

**Usage:**
```bash
./mcp-start.sh
# Or configured as MCP server command in Claude Code settings
```

---

## scripts/start_splade_server.sh

**Purpose:** Start the SPLADE sparse embedding server as a standalone process.
**Input:** None (no arguments). Requires `venv/` and the SPLADE model (downloads from HuggingFace on first run).
**Output:** Running uvicorn server on port 8083 (`src.rag.splade_server:app`).

**Usage:**
```bash
bash scripts/start_splade_server.sh
```
