# RAG System for Claude Code

Vector-based retrieval system exposing search via MCP for Claude Code agents.

## Stack

| Component | Choice |
|-----------|--------|
| PDF Extraction | MinerU (../Mineru/) |
| Embedding | Qwen3-Embedding-8B (native llama.cpp + Metal GPU) |
| Vector DB | PostgreSQL + pgvector |
| MCP | FastMCP |

## Quick Start

```bash
./start.sh
```

Starts: PostgreSQL (Docker, port 5433) + llama.cpp embedding server (native, port 8081)

## Pipeline

### Full Flow (PDF to RAG)

```
PDF
 | MinerU (../Mineru/workflow.py)
 v
raw MD
 | postprocess.py (structural cleanup)
 v
data/documents/<name>/raw.md
 | chunker.py
 v
chunks
 | md-cleanup agent (LLM cleanup per chunk)
 v
data/documents/<name>/chunks.json
 | indexer.py
 v
pgvector
```

**Use:** `/pdf-to-rag /path/to/file.pdf`

### Document Structure

```
data/documents/
├── paper1/
│   ├── raw.md        # After postprocess (human-readable)
│   └── chunks.json   # After LLM cleanup (indexed)
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
    {"index": 1, "content": "..."}
  ]
}
```

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
│   ├── raw/              # Temporary MinerU outputs
│   └── documents/        # Document folders (raw.md + chunks.json)
└── src/rag/              # [See DOCS.md](src/rag/DOCS.md)
```

## Usage

### Index from JSON (Recommended)

```bash
./venv/bin/python workflow.py index-json --input ./data/documents/paper1/chunks.json
```

### Index from Directory (Legacy)

```bash
./venv/bin/python workflow.py index --input-dir ./data/documents
```

Re-chunks files. Use `index-json` for pre-chunked content.

### Search

```bash
./venv/bin/python workflow.py search --query "your query" --top-k 5
```

## Build llama.cpp (if needed)

```bash
cd llama.cpp
cmake -B build -DGGML_METAL=ON
cmake --build build --config Release -j --target llama-server
```
