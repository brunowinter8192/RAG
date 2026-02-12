# RAG System for Claude Code

Vector-based retrieval system exposing search via MCP for Claude Code agents.

## Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| PDF Extraction | MinerU (../Mineru/) | Best open-source PDF extraction |
| Embedding Model | Qwen3-Embedding-8B | #1 MTEB, Programming Languages support, 32K context |
| Vector DB | PostgreSQL 18 + pgvector 0.8 | Production-ready, native SQL, HNSW index support |
| MCP Framework | FastMCP | Consistent with other MCP servers |

### Chunking

Semantic chunking: Splits at paragraph boundaries (`\n\n`), then sentences, with 200 char overlap.

## Quick Start

### 1. Clone + Python Setup

Requires Python >= 3.10, Docker, and [llama.cpp](https://github.com/ggml-org/llama.cpp).

```bash
git clone https://github.com/brunowinter8192/RAG-MCP.git
cd RAG-MCP
python -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env
```

### 2. Vector Database

Start PostgreSQL with pgvector (see [PostgreSQL Configuration](#postgresql-18-volume-path) for version details):

```bash
docker compose up -d postgres
```

### 3. Embedding Model

Download a GGUF embedding model and build llama.cpp (see [Embedding Server](#embedding-server-llamacpp) for model choices and build instructions):

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

### 7. Claude Code Integration

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

## Prerequisites Check

Verify services are running:

```bash
# PostgreSQL
docker ps --filter name=rag-postgres --format "{{.Names}}: {{.Status}}"

# llama.cpp embedding server
curl -s localhost:8081/health
```

| Service | Port | Required For |
|---------|------|--------------|
| PostgreSQL | 5433 | Index + Search |
| llama.cpp | 8081 | Index + Search |

## Pipeline

### Full Flow (PDF to RAG)

```
PDF
 ↓ MinerU (optional, for PDF extraction)
 ↓ postprocess.py (generic regex cleanup)
raw.md
 ↓ LLM cleanup (optional)
cleaned.md
 ↓ chunker.py
chunks.json
 ↓ indexer.py
pgvector
```

**Note:** MinerU is only required for the PDF-to-Markdown step. You can start at any point in the pipeline -- feed Markdown files directly to the chunker, or pre-chunked JSON directly to the indexer.

**Module details:** [src/rag/DOCS.md](src/rag/DOCS.md)

### Document Structure

```
data/documents/
├── paper1/
│   ├── raw.md        # After MinerU + generic postprocess
│   ├── cleaned.md    # After LLM cleanup (agent script)
│   └── chunks.json   # Chunked for indexing
├── paper2/
│   └── ...
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

**Per-Chunk Document Field:** Optional `document` per chunk. Falls vorhanden, wird es statt top-level verwendet. Ermöglicht Multi-File-Collections (mehrere MD-Files → 1 Collection mit N Documents).

## Entry Points

| Entry Point | Purpose | Trigger |
|-------------|---------|---------|
| `server.py` | MCP server - exposes `search` tool to Claude Code | Claude Code (via .mcp.json) |
| `workflow.py` | Pipeline CLI - chunking, indexing, search | Human (terminal) |

## Directory Structure

```
RAG/
├── server.py              # MCP Entry Point (Claude Code)
├── workflow.py            # Pipeline Entry Point (CLI)
├── start.sh               # Start all services
├── docker-compose.yml     # PostgreSQL only
├── llama.cpp/             # Native embedding server (Metal GPU)
├── models/                # GGUF model files
├── data/documents/        # Document folders (raw.md, cleaned.md, chunks.json)
├── debug/                 # Agent-generated cleanup scripts (gitignored)
└── src/rag/               [See DOCS.md](src/rag/DOCS.md)
```

**Details:** [src/rag/DOCS.md](src/rag/DOCS.md)

## Build llama.cpp

See [Quick Start Step 3](#3-embedding-model) for download + build commands.

## System Configuration

### Development Hardware

MacBook Pro M4 Pro, 14 Cores, 48GB Unified Memory

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

Host path: `/var/lib/docker/volumes/rag_rag_postgres_data/_data`

### PostgreSQL Connection: Docker Exec Required

Direct psycopg2 connections from host to container may fail with authentication errors, even with correct credentials. Use `docker exec` for database operations:

```bash
# WORKS - via docker exec
docker exec rag-postgres psql -U rag -d rag -c "SELECT COUNT(*) FROM documents;"

# MAY FAIL - direct connection from host
psycopg2.connect(host='localhost', port=5433, user='rag', password='rag', dbname='rag')
```

The workflow.py and server.py handle this internally. For manual operations, always use docker exec.

### Checking PostgreSQL: Docker vs CLI

`psql --version` shows the **client** version (Homebrew), not the server.

```bash
# Client version (Homebrew) - NOT the running server
psql --version
# → psql (PostgreSQL) 17.6 (Homebrew)

# Actual server version (Docker container)
docker ps --filter name=postgres --format "{{.Names}}: {{.Image}}"
# → rag-postgres: pgvector/pgvector:pg18
```

Always use `docker ps` to verify the actual PostgreSQL server version.

### Embedding Server (llama.cpp)

**Model:** [Qwen3-Embedding-8B](https://huggingface.co/Qwen/Qwen3-Embedding-8B-GGUF) - #1 MTEB Multilingual Leaderboard

**Quantization Quality:**

| Quant | Bits | Size | Quality | Recommendation |
|-------|------|------|---------|----------------|
| F16/BF16 | 16 | 15.1 GB | 100% | Gold standard |
| Q8_0 | 8 | 8.05 GB | ~99.9% | **Sweet spot** |
| Q5_K_M | 5 | 5.42 GB | ~96-98% | Acceptable |
| Q4_K_M | 4 | 4.68 GB | ~90-95% | Noticeable loss |

**Q8_0 = "Near-FP16":** 8-bit quantization mit nur +0.001 Perplexity-Unterschied zu FP16. Praktisch identische Embedding-Qualität bei halber Größe.

Source: [llama.cpp Quantization](https://github.com/ggml-org/llama.cpp/discussions/2094)

**SOTA Config:**

```bash
./llama.cpp/build/bin/llama-server \
  -m ./models/Qwen3-Embedding-8B-Q8_0.gguf \
  --embedding \
  --host 0.0.0.0 \
  --port 8081 \
  -ngl 99 \        # Full GPU offload (Metal)
  -ub 4096 \       # ubatch size
  -b 4096          # batch size
```

Source: [Qwen llama.cpp Guide](https://qwen.readthedocs.io/en/latest/quantization/llama.cpp.html)

**Download Q8_0:**

```bash
huggingface-cli download Qwen/Qwen3-Embedding-8B-GGUF \
  Qwen3-Embedding-8B-Q8_0.gguf --local-dir ./models/
```
