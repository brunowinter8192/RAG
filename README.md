# RAG

Local RAG pipeline for Claude Code — index PDFs and websites, search with hybrid retrieval.

## Features

- **Hybrid Search** — dense vectors + sparse keywords + cross-encoder reranking, fused with RRF
- **PDF→RAG Pipeline** — MinerU extraction → LLM cleanup → chunking → indexing
- **Web→RAG Pipeline** — crawled markdown → cleanup → chunking → indexing
- **Auto-Start** — GPU embedding and reranker servers start on demand, stop after 15 minutes idle
- **Multi-Collection** — multiple document collections, searchable independently or together

## Quick Start

```
/plugin marketplace add brunowinter8192/claude-plugins
/plugin install rag
# Restart session

# Index a PDF:
/rag:pdf-convert /path/to/document.pdf

# Search is handled by the rag-search agent automatically
```

## Prerequisites

- Docker (for PostgreSQL + pgvector)
- [llama.cpp](https://github.com/ggml-org/llama.cpp) built with GPU support (Metal/CUDA)
- Python 3.11+

You choose your own models — any llama-server-compatible GGUF works for embedding and reranking. SPLADE uses a fixed HuggingFace model that auto-downloads. All model paths and ports are configured in `.env`.

`mcp-start.sh` auto-starts PostgreSQL and GPU servers on each session. Manual setup is only needed for first-time installation.

## Setup

**1. Clone + venv**

```bash
git clone https://github.com/brunowinter8192/RAG.git
cd RAG
python -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env
```

**2. Configure `.env`**

Edit `.env` to set your model paths and ports. See `.env.example` for all available options. Key settings:

| Variable | What it does |
|----------|-------------|
| `EMBEDDING_MODEL_PATH` | Path to your embedding GGUF model |
| `RERANKER_MODEL_PATH` | Path to your reranker GGUF model |
| `LLAMA_SERVER_PATH` | Path to your llama-server binary |
| `VECTOR_DIMENSION` | Must match your embedding model's output dimension |

Defaults point to `./models/` and `./llama.cpp/build/bin/llama-server`. Ports default to 8081 (embedding), 8082 (reranker), 8083 (SPLADE).

**3. Start PostgreSQL**

```bash
docker compose up -d postgres
```

**4. Build llama.cpp**

```bash
cd llama.cpp
cmake -B build -DGGML_METAL=ON    # or -DGGML_CUDA=ON for NVIDIA
cmake --build build --config Release -j --target llama-server
cd ..
```

**5. Download models**

Choose any llama-server-compatible GGUF models. Example (our setup):

```bash
# Embedding (4096 dimensions)
huggingface-cli download Qwen/Qwen3-Embedding-8B-GGUF \
  Qwen3-Embedding-8B-Q8_0.gguf --local-dir ./models/

# Reranker (auto-downloads on first use if using Qwen3-Reranker-0.6B)
```

Update `EMBEDDING_MODEL_PATH` and `RERANKER_MODEL_PATH` in `.env` to match your downloaded files.

## Usage

### MCP Tools

| Tool | What it does | When to use |
|------|-------------|-------------|
| `search_hybrid` | Hybrid semantic + keyword search with RRF fusion and cross-encoder reranking | Default choice for any collection |
| `search` | Pure semantic vector search | Conceptual questions, no exact terms needed |
| `search_keyword` | Exact term matching with stemming | Technical terms, function names, identifiers |
| `read_document` | Read continuous chunks from a document | After search: expand context around a hit |
| `list_collections` | Show all indexed collections with chunk counts | Discover what's available |
| `list_documents` | Show documents in a collection | Inspect a collection before filtering |

### Skills & Commands

- `/rag:pdf-convert` — Full PDF→RAG pipeline. Extracts PDF with MinerU, cleans markdown with LLM agent, chunks and indexes into PostgreSQL. Runs in phases with stop points for verification.
- `/rag:web-md-index` — Website markdown→RAG pipeline. Cleans crawled markdown (removes navigation, footers, UI chrome), then chunks and indexes.

### Agents

- **rag-search** — Autonomous search agent. Handles collection discovery, multi-query search strategy, and deep reading via `read_document`. Dispatched automatically when RAG search is needed.
- **md-cleanup-master** — Cleans PDF-converted markdown. Fixes OCR artifacts, broken images, spaced LaTeX, and split words.
- **web-md-cleanup** — Cleans website-crawled markdown. Removes navigation blocks, footers, UI chrome, and duplicate table-of-contents.

## Workflows

**PDF → RAG**

1. PDF extraction (MinerU) → raw markdown
2. LLM cleanup (md-cleanup-master agent) → clean markdown
3. Chunking + dense/sparse embedding → PostgreSQL with pgvector
4. Ready to search via MCP tools

**Website → RAG**

1. Crawl website (e.g. via SearXNG `/crawl-site`) → markdown files
2. LLM cleanup (web-md-cleanup agent) → clean markdown
3. Chunking + dense/sparse embedding → PostgreSQL
4. Ready to search via MCP tools

## Troubleshooting

<details>
<summary>PostgreSQL connection refused</summary>

The database container is not running.

```bash
docker compose up -d postgres
```

Verify: `docker ps --filter name=rag-postgres`

</details>

<details>
<summary>Embedding server not responding (port 8081)</summary>

`mcp-start.sh` starts the embedding server automatically. For manual start:

```bash
./venv/bin/python workflow.py server start
```

Check status:

```bash
./venv/bin/python workflow.py server status
curl -s localhost:8081/health
```

</details>

<details>
<summary>Reranker slow on first search</summary>

The reranker model (Qwen3-Reranker-0.6B, ~600MB) downloads on first use. Subsequent calls are fast. This is expected behavior — no action needed.

</details>

<details>
<summary>Search returns empty results</summary>

1. Verify the collection exists: `list_collections()` (no GPU servers needed)
2. Check that GPU servers are running: `./venv/bin/python workflow.py server status`
3. If servers are down: `./venv/bin/python workflow.py server start`

</details>

## License

MIT
