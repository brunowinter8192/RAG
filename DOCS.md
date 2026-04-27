# RAG — Root Modules

## Documentation Tree

- [src/rag/DOCS.md](src/rag/DOCS.md) — RAG pipeline modules (retrieval, indexing, embedding, server lifecycle)
- [dev/DOCS.md](dev/DOCS.md) — Development & evaluation scripts

---

## cli.py

**Purpose:** LLM-facing CLI entry point — 6 retrieval subcommands consumed by the `agent-rag-search` Skill via the `rag-cli` wrapper (`~/.local/bin/rag-cli` in PATH).
**Input:** Subcommand + positional args (query, collection, filters, options).
**Output:** Stdout — formatted search results, document content, or listings.

| Subcommand | Description |
|---|---|
| `search` | Dense vector search (cosine similarity) |
| `search_hybrid` | Dense + SPLADE + CC fusion; optional cross-encoder reranking |
| `search_keyword` | BM25 full-text keyword search |
| `list_collections` | All indexed collections with chunk counts |
| `list_documents` | Documents in a collection |
| `read_document` | Anchor chunk plus N chunks before and M chunks after |

**Usage (via `rag-cli` wrapper):**
```bash
rag-cli list_collections
rag-cli list_documents my_collection
rag-cli search_hybrid "transformer attention" my_collection --top-k 20
rag-cli search "semantic similarity" my_collection --top-k 30
rag-cli search_keyword "learning_rate dropout" my_collection --top-k 20
rag-cli read_document my_collection paper.md 42 --before 2 --after 5
```

---

## workflow.py

**Purpose:** Human-triggered pipeline CLI — chunking, indexing, search, SPLADE backfill, collection management, and GPU server control. Not LLM-facing.
**Input:** CLI arguments (subcommands below).
**Output:** Stdout — progress messages, search results, server status, or deletion counts.

| Subcommand | Description |
|---|---|
| `index-dir` | Chunk + index all `.md` files in a directory (handles server startup) |
| `index-json` | Index chunks from a pre-chunked `chunks.json` file |
| `search` | Dense search query with printed results |
| `chunk` | Chunk a markdown file → writes `chunks.json` |
| `backfill-splade` | Fill NULL sparse embeddings for an existing collection |
| `delete` | Delete chunks by collection and/or document |
| `server` | GPU server control — status / start / stop / restart [name] |

**Usage:**
```bash
./venv/bin/python workflow.py index-dir --input data/documents/MyCollection/
./venv/bin/python workflow.py index-dir --input data/documents/papers/ --collection my_collection
./venv/bin/python workflow.py index-json --input data/documents/MyCollection/chunks.json
./venv/bin/python workflow.py search --query "hybrid retrieval" --collection RAG_MCP --top-k 5
./venv/bin/python workflow.py chunk --input data/documents/MyCollection/doc.md
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
**Output:** Running PostgreSQL + all GPU servers (embedding port 8081, reranker 8082, SPLADE 8083).

**Usage:**
```bash
./start.sh
```
