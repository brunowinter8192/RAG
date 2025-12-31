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

## Prerequisites Check

Before indexing/searching, verify services are running:

```bash
# PostgreSQL (should show rag-postgres as healthy)
docker ps --filter name=rag-postgres --format "{{.Names}}: {{.Status}}"

# llama.cpp embedding server (should show llama-ser on port 8081)
lsof -i :8081 | head -2
```

| Service | Port | Required For |
|---------|------|--------------|
| PostgreSQL | 5433 | Index + Search |
| llama.cpp | 8081 | Index + Search |

```bash
# Check indexed documents
docker exec rag-postgres psql -U rag -d rag -c "SELECT source, COUNT(*) as chunks FROM documents GROUP BY source;"
```

## Pipeline

### Full Flow (PDF to RAG)

```
PDF
 ↓ MinerU (../Mineru/workflow.py)
 ↓ postprocess.py (generic regex cleanup)
raw.md
 ↓ md-cleanup-master (creates debug/clean_<name>.py)
cleaned.md
 ↓ chunker.py
chunks.json
 ↓ indexer.py
pgvector
```

**Use:** `/pdf-convert /path/to/file.pdf`

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
├── data/documents/        # Document folders (raw.md, cleaned.md, chunks.json)
├── debug/                 # Agent-generated cleanup scripts (gitignored)
└── src/rag/               [See DOCS.md](src/rag/DOCS.md)
```

**Details:** [src/rag/DOCS.md](src/rag/DOCS.md)

## Usage

### Index from JSON (Recommended)

```bash
./venv/bin/python workflow.py index-json --input ./data/documents/paper1/chunks.json
```

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
