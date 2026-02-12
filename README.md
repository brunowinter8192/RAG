# RAG System for Claude Code

Vector-based retrieval system exposing search via MCP for Claude Code agents.

## Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| PDF Extraction | MinerU | Best open-source PDF extraction |
| Embedding Model | Qwen3-Embedding-8B | #1 MTEB, Programming Languages support, 32K context |
| Vector DB | PostgreSQL 18 + pgvector 0.8 | Production-ready, native SQL, HNSW index support |
| MCP Framework | FastMCP | Consistent with other MCP servers |

## Installation

### As Plugin (recommended)

In a Claude Code session:

```
/plugin marketplace add brunowinter8192/claude-plugins
/plugin install rag
```

Restart the session after installation.

### Manual (.mcp.json)

Add to your project's `.mcp.json` (all paths must be absolute):

```json
{
  "mcpServers": {
    "rag": {
      "command": "/absolute/path/to/RAG/venv/bin/fastmcp",
      "args": ["run", "/absolute/path/to/RAG/server.py"]
    }
  }
}
```

## Plugin Components

| Component | Name | Description |
|-----------|------|-------------|
| **Skill** | `/rag:mcp_usage` | Tool usage strategy, parameters, examples, score interpretation |
| **Command** | `/rag:pdf-convert` | Full PDF-to-RAG pipeline (extract, chunk, index) |
| **MCP Server** | `rag` | 3 search tools over indexed documents |

## MCP Tools

### search

Semantic search over indexed documents using vector embeddings.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query (natural language) |
| `top_k` | int | No | 5 | Number of results (1-20) |
| `collection` | string | No | all | Filter by collection name |
| `document` | string | No | all | Filter by document name |

```
mcp__rag__search(query="TPC-H benchmark performance", top_k=3)
mcp__rag__search(query="pricing requirements", collection="specification")
```

### list_collections

List all indexed collections with chunk counts. No parameters.

### list_documents

List documents in a collection with chunk counts.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `collection` | string | Yes | Collection name |

## Prerequisites

| Service | Port | Required For |
|---------|------|--------------|
| PostgreSQL 18 + pgvector | 5433 | Index + Search |
| llama.cpp embedding server | 8081 | Index + Search |

Verify services are running:

```bash
docker ps --filter name=rag-postgres --format "{{.Names}}: {{.Status}}"
curl -s localhost:8081/health
```

## Setup

### 1. Clone + Python

Requires Python >= 3.10, Docker, and [llama.cpp](https://github.com/ggml-org/llama.cpp).

```bash
git clone https://github.com/brunowinter8192/RAG.git
cd RAG
python -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env
```

### 2. Vector Database

```bash
docker compose up -d postgres
```

### 3. Embedding Model

```bash
# Build llama.cpp (macOS Metal example)
cd llama.cpp
cmake -B build -DGGML_METAL=ON
cmake --build build --config Release -j --target llama-server
cd ..

# Download model
huggingface-cli download Qwen/Qwen3-Embedding-8B-GGUF \
  Qwen3-Embedding-8B-Q8_0.gguf --local-dir ./models/
```

### 4. Start Services

```bash
./start.sh
```

Starts: PostgreSQL (Docker, port 5433) + llama.cpp embedding server (native, port 8081)

### 5. Index Documents

```bash
./venv/bin/python workflow.py index-json --input ./data/documents/myproject/chunks.json
```

### 6. Search

```bash
./venv/bin/python workflow.py search --query "your query" --top-k 5
```

## Pipeline

### Full Flow (PDF to RAG)

```
PDF
 | MinerU (optional, for PDF extraction)
 | postprocess.py (generic regex cleanup)
raw.md
 | LLM cleanup (optional)
cleaned.md
 | chunker.py
chunks.json
 | indexer.py
pgvector
```

MinerU is only required for the PDF-to-Markdown step. You can start at any point in the pipeline -- feed Markdown files directly to the chunker, or pre-chunked JSON directly to the indexer.

Semantic chunking: Splits at paragraph boundaries (`\n\n`), then sentences, with 200 char overlap.

**Module details:** [src/rag/DOCS.md](src/rag/DOCS.md)

### Document Structure

```
data/documents/
  paper1/
    raw.md        # After MinerU + generic postprocess
    cleaned.md    # After LLM cleanup (agent script)
    chunks.json   # Chunked for indexing
  paper2/
    ...
```

### chunks.json Format

```json
{
  "source_pdf": "/original/path/to/file.pdf",
  "created": "2025-12-28T...",
  "chunks": [
    {"index": 0, "content": "..."},
    {"index": 1, "content": "...", "document": "chapter2.md"}
  ]
}
```

Optional `document` field per chunk overrides the top-level source. Enables multi-file collections (multiple MD files in one collection with N documents).

## Entry Points

| Entry Point | Purpose | Trigger |
|-------------|---------|---------|
| `server.py` | MCP server - exposes search tools to Claude Code | Claude Code (via plugin or .mcp.json) |
| `workflow.py` | Pipeline CLI - chunking, indexing, search | Human (terminal) |

## Directory Structure

```
RAG/
  .claude-plugin/          # Plugin manifest (plugin.json only)
  commands/                # Plugin commands (pdf-convert)
  skills/                  # Plugin skills (mcp_usage)
  server.py                # MCP Entry Point (Claude Code)
  workflow.py              # Pipeline Entry Point (CLI)
  start.sh                 # Start all services
  docker-compose.yml       # PostgreSQL only
  llama.cpp/               # Native embedding server (Metal GPU)
  models/                  # GGUF model files
  data/documents/          # Document folders (raw.md, cleaned.md, chunks.json)
  src/rag/                 # Module implementations (see DOCS.md)
```

**Module details:** [src/rag/DOCS.md](src/rag/DOCS.md)

## System Configuration

### PostgreSQL 18 Volume Path

PostgreSQL 18 changed the data directory structure. Volume must mount at `/var/lib/postgresql` (not `/var/lib/postgresql/data`).

```yaml
# CORRECT (PG18+)
volumes:
  - rag_postgres_data:/var/lib/postgresql

# WRONG (causes container crash on PG18)
volumes:
  - rag_postgres_data:/var/lib/postgresql/data
```

See: https://github.com/docker-library/postgres/pull/1259

### PostgreSQL Connection: Docker Exec Required

Direct psycopg2 connections from host to container may fail with authentication errors. Use `docker exec` for manual database operations:

```bash
docker exec rag-postgres psql -U rag -d rag -c "SELECT COUNT(*) FROM documents;"
```

The workflow.py and server.py handle connections internally.

### Embedding Server (llama.cpp)

**Model:** [Qwen3-Embedding-8B](https://huggingface.co/Qwen/Qwen3-Embedding-8B-GGUF) - #1 MTEB Multilingual Leaderboard

| Quant | Bits | Size | Quality | Recommendation |
|-------|------|------|---------|----------------|
| F16/BF16 | 16 | 15.1 GB | 100% | Gold standard |
| Q8_0 | 8 | 8.05 GB | ~99.9% | **Sweet spot** |
| Q5_K_M | 5 | 5.42 GB | ~96-98% | Acceptable |
| Q4_K_M | 4 | 4.68 GB | ~90-95% | Noticeable loss |

**Server config:**

```bash
./llama.cpp/build/bin/llama-server \
  -m ./models/Qwen3-Embedding-8B-Q8_0.gguf \
  --embedding \
  --host 0.0.0.0 \
  --port 8081 \
  -ngl 99 \
  -ub 4096 \
  -b 4096
```
