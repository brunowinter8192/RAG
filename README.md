# RAG System for Claude Code

Vector-based retrieval system exposing search via MCP for Claude Code agents.

## Stack

| Component | Choice |
|-----------|--------|
| Embedding | Qwen3-Embedding-8B (native llama.cpp + Metal GPU) |
| Vector DB | PostgreSQL + pgvector |
| MCP | FastMCP |

## Quick Start

```bash
# Start services
./start.sh
```

This starts:
- PostgreSQL (Docker, port 5433)
- llama.cpp embedding server (native, port 8081)

## Directory Structure

```
RAG/
├── server.py              # MCP Server
├── workflow.py            # CLI for indexing/search
├── start.sh               # Start all services
├── docker-compose.yml     # PostgreSQL only
├── llama.cpp/             # Native embedding server (Metal GPU)
├── models/                # GGUF model files
├── data/
│   ├── raw/              # MinerU outputs
│   └── documents/        # Cleaned MDs for indexing
└── src/rag/              # [See DOCS.md](src/rag/DOCS.md)
```

## Usage

### Index Documents

```bash
./venv/bin/python workflow.py index --input-dir ./data/documents
```

### Search

```bash
./venv/bin/python workflow.py search --query "your query" --top-k 5
```

### PDF to RAG (Slash Command)

```
/pdf-to-rag /path/to/file.pdf
```

## Build llama.cpp (if needed)

```bash
cd llama.cpp
cmake -B build -DGGML_METAL=ON
cmake --build build --config Release -j --target llama-server
```
