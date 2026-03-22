# src/rag/ - RAG Pipeline Modules

## Working Directory

```
cd /path/to/MCP/RAG
```

## Directory Structure

```
src/rag/
├── __init__.py
├── chunker.py
├── embedder.py
├── indexer.py
├── reranker.py
├── retriever.py
├── server_manager.py
├── sparse_embedder.py
├── splade_server.py
└── logs/
```

---

## embedder.py

**Purpose:** Generate embeddings via llama.cpp server (HTTP API).

**Input:** Text or list of texts
**Output:** List of embedding vectors (list[list[float]])

**Usage:**
```python
from src.rag.embedder import embed_workflow

embeddings = embed_workflow("Your text here")
embeddings = embed_workflow(["Text 1", "Text 2"])

# With Qwen3 instruct prefix (used internally by retriever.py)
embeddings = embed_workflow("Your text", prefix="Instruct: ...\nQuery: ")
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| texts | str \| list[str] | required | Text or list of texts to embed |
| prefix | str \| None | None | Optional prefix prepended to each text (e.g., Qwen3 instruct format) |

**Token Truncation:**

Texts are automatically truncated to ~MAX_TOKENS (4000) before embedding using character-based estimation (no API calls).

```python
truncate_to_max_tokens(text: str, max: int) -> str  # Truncate using char estimate
```

**Environment Variables (.env):**
| Variable | Default | Description |
|----------|---------|-------------|
| EMBEDDING_URL | http://localhost:8081/v1/embeddings | llama.cpp server endpoint |
| EMBEDDING_MODEL | Qwen3-Embedding-8B | Model name for API |

**Constants:**
| Constant | Value | Description |
|----------|-------|-------------|
| MAX_TOKENS | 4000 | Max tokens per embedding request |
| CHARS_PER_TOKEN | 3 | Conservative char/token ratio for truncation |

**Server lifecycle:** Managed by `server_manager.py`. Auto-starts via `ensure_ready("embedding")`, auto-stops after idle timeout.

---

## chunker.py

**Purpose:** Split documents into semantic chunks for embedding.

**Input:** File path, chunking strategy
**Output:** List of chunk dicts with content and metadata

**Usage:**
```python
from src.rag.chunker import chunk_workflow

chunks = chunk_workflow("docs/readme.md")
chunks = chunk_workflow("docs/readme.md", chunk_size=1500, overlap=200)
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| file_path | str | required | Path to file to chunk |
| chunk_size | int | 1000 | Max characters per chunk |
| overlap | int | 200 | Overlap between chunks (word-aligned) |

**Chunking (Recursive Split — semantic boundaries):**

Uses hierarchical separators to split at natural boundaries:
1. `\n\n` (paragraphs)
2. `\n` (lines)
3. `. ` / `! ` / `? ` (sentences)
4. ` ` (words - last resort)

Chunks never break mid-sentence. If a paragraph exceeds chunk_size, it splits at sentence boundaries first.

**Overlap Handling:**

Overlap text is aligned to word boundaries to prevent mid-word cuts:
```python
get_word_aligned_overlap(text, overlap) -> str  # Returns overlap starting at word boundary
```

**Constants:**
| Constant | Value | Description |
|----------|-------|-------------|
| DEFAULT_CHUNK_SIZE | 1000 | Max characters per chunk |
| DEFAULT_OVERLAP | 200 | Overlap between chunks (word-aligned) |

**CLI Usage (via workflow.py):**
```bash
./venv/bin/python workflow.py chunk --input docs/readme.md --chunk-size 1500 --overlap 200
```

Produces a JSON file at the same path with `.json` extension, compatible with `index-json`:
```json
{"document": "readme.md", "chunks": [{"index": 0, "content": "..."}]}
```

| Flag | Default | Description |
|------|---------|-------------|
| --input | required | Path to markdown file |
| --chunk-size | 1000 | Target chunk size in chars |
| --overlap | 200 | Overlap between chunks |
| --document | input filename | Document name in JSON output |

---

## splade_server.py

**Purpose:** Standalone FastAPI server generating SPLADE sparse embeddings.

**Model:** `naver/splade-cocondenser-ensembledistil` (110M params, CC BY-NC-SA)
**Port:** 8083 (configurable via env `SPLADE_PORT`)

**Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Returns `{"status": "ok"}` |
| `/v1/sparse-embeddings` | POST | Generate sparse embeddings |

**Request:**
```json
{"input": ["text1", "text2"], "model": "splade"}
```

**Response:**
```json
{"data": [{"index": 0, "sparse_vector": {"indices": [1, 42, 7891], "values": [0.82, 0.31, 0.15]}}]}
```

**Startup:**
```bash
bash scripts/start_splade_server.sh
# or
./venv/bin/python -m uvicorn src.rag.splade_server:app --host 0.0.0.0 --port 8083
```

Model loaded once at module level (not per request). First start downloads model from HuggingFace (~440MB).

---

## server_manager.py

**Purpose:** Centralized lifecycle management for all GPU servers (embedding, SPLADE, reranker). Single source of truth for server configs, ports, and startup commands.

**Key functions:**

| Function | Description |
|----------|-------------|
| `status()` | Returns running/stopped state, PID, health for all servers |
| `start(name)` | Start a server with port-check (no duplicates) |
| `stop(name)` | Stop all processes on a server's port |
| `restart(name)` | Stop + start |
| `ensure_ready(target)` | Auto-start server(s) needed for an operation, touch idle timestamp |
| `start_all()` / `stop_all()` | Batch operations |

**Idle timeout:** Servers auto-stop after 5 minutes without use. Configurable via `RAG_SERVER_IDLE_TIMEOUT` env var (seconds). Cross-project aware via shared timestamp files (`/tmp/rag-server-{name}-last-used`).

**Server definitions:**

| Server | Port | Model | Required for |
|--------|------|-------|-------------|
| embedding | 8081 | Qwen3-Embedding-8B-Q8_0 | search, index |
| reranker | 8082 | qwen3-reranker-0.6b-q8_0 | rerank |
| splade | 8083 | naver/splade-cocondenser-ensembledistil | search, index |

**CLI:** `./venv/bin/python workflow.py server status|start|stop|restart [name]`

---

## sparse_embedder.py

**Purpose:** HTTP client for SPLADE server (port 8083). Mirrors `embedder.py` pattern.

**Input:** Text or list of texts
**Output:** List of sparse vector dicts `[{"indices": [...], "values": [...]}]`

**Usage:**
```python
from src.rag.sparse_embedder import sparse_embed_workflow

sparse_vecs = sparse_embed_workflow("Your text here")
sparse_vecs = sparse_embed_workflow(["Text 1", "Text 2"])
```

**Server lifecycle:** Managed by `server_manager.py`. Auto-starts via `ensure_ready("splade")`, auto-stops after idle timeout.

**Environment Variables (.env):**
| Variable | Default | Description |
|----------|---------|-------------|
| SPLADE_URL | http://localhost:8083/v1/sparse-embeddings | SPLADE server endpoint |

---

## indexer.py

**Purpose:** Index documents into PostgreSQL with pgvector. Handles schema creation, batch embedding + insert, SPLADE backfill, and deletion by collection/document.
**Input:** Path to `chunks.json` (index), collection name (backfill/delete), or collection+document pair (delete).
**Output:** Count of indexed or deleted chunks.

### Environment Variables (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| POSTGRES_HOST | localhost | PostgreSQL host |
| POSTGRES_PORT | 5433 | PostgreSQL port (Docker-mapped) |
| POSTGRES_USER | rag | Database user |
| POSTGRES_PASSWORD | rag | Database password |
| POSTGRES_DB | rag | Database name |
| VECTOR_DIMENSION | 4096 | Vector dimension |

### Schema

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    collection TEXT NOT NULL,
    document TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    total_chunks INTEGER NOT NULL,
    embedding vector(4096),
    tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    sparse_embedding sparsevec(30522)
)
```

**Indexes:**
```sql
CREATE INDEX idx_documents_tsv ON documents USING gin(tsv);
CREATE UNIQUE INDEX idx_documents_unique ON documents(collection, document, chunk_index);
```

All schema elements are created automatically by `ensure_schema()` in `indexer.py` (idempotent — safe to run on existing databases).

---

## reranker.py

**Purpose:** Re-score search results using a cross-encoder model via llama.cpp server (HTTP API).

**Input:** Query string, list of document dicts, top_k
**Output:** Top-k documents re-scored by cross-encoder relevance

**Usage:**
```python
from src.rag.reranker import rerank_workflow

# Rerank search results for higher precision
reranked = rerank_workflow("authentication patterns", search_results, top_k=5)
```

**How it works:**
1. Extracts `content` from each document dict
2. Sends query + documents to `/v1/rerank` endpoint
3. Maps relevance scores back to original document dicts
4. Returns top_k sorted by relevance score (descending)

**Model:** Qwen3-Reranker-8B (GGUF Q8_0, ~7.5GB). Self-converted from HF (`convert_hf_to_gguf.py` → f16, then `llama-quantize` → Q8_0). Verified against Issue #16407 test data — ranking identical to official ggml-org 0.6B.

**Server:** Second llama-server instance (Homebrew) on port 8082 with `--rerank -c 4096 --no-webui` flags. Auto-started on first use (same pattern as embedder.py).

**Environment Variables (.env):**
| Variable | Default | Description |
|----------|---------|-------------|
| RERANKER_URL | http://localhost:8082/v1/rerank | llama.cpp reranker endpoint |

**Constants:**
| Constant | Value | Description |
|----------|-------|-------------|
| RERANKER_HEALTH_URL | http://localhost:8082/health | Health check endpoint |
| RERANKER_MODEL_PATH | models/Qwen3-Reranker-8B-Q8_0.gguf | Model file path |

---

## retriever.py

**Purpose:** Search indexed documents via vector cosine similarity.

**Input:** Query string, optional filters
**Output:** List of matching chunks with scores

**Usage:**
```python
from src.rag.retriever import search_workflow

# Basic search
results = search_workflow("How to configure authentication?", top_k=5)

# Filter by collection
results = search_workflow("pricing", top_k=5, collection="specification")

# Filter by document
results = search_workflow("query execution", collection="specification", document="specification.md")

# With context expansion (include neighboring chunks)
results = search_workflow("authentication", top_k=3, neighbors=1)
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| query | str | required | Search query |
| top_k | int | 5 | Number of results (max 20) |
| collection | str | None | Filter by collection name |
| document | str | None | Filter by document name |
| neighbors | int | 0 | Include N chunks before/after each match (0-2) |

**Context Expansion:**

When `neighbors > 0`, each result's content is expanded to include adjacent chunks:
- `neighbors=1`: Returns [prev_chunk + match + next_chunk]
- `neighbors=2`: Returns [prev-2 + prev-1 + match + next+1 + next+2]

**Behavior:**
- Chunks concatenated with `\n\n`
- Overlapping matches are deduplicated and merged into contiguous blocks
- Results sorted by document order (collection, document, chunk_index)
- Edge cases (first/last chunk) handled automatically

**Output Format:**
```python
[
    {
        "content": "The actual chunk text...",
        "collection": "specification",
        "document": "specification.md",
        "chunk_index": 0,
        "score": 0.8742  # cosine similarity (1 - distance)
    }
]
```

**Score Filtering:** Results below 0.5 cosine similarity are automatically removed.

**Collection Validation:** Raises `ValueError` if collection doesn't exist (lists available collections in error message).

**Environment Variables:** Same as indexer.py (PostgreSQL connection)

**Constants:**
| Constant | Value | Description |
|----------|-------|-------------|
| HYBRID_CANDIDATES | 50 | Number of candidates per search method for RRF fusion |
| RERANK_CANDIDATES | 50 | Number of RRF candidates sent to cross-encoder for reranking |
| RRF_K | 60 | RRF smoothing constant |
| DEFAULT_QUERY_PREFIX | `"Instruct: Given a search query, retrieve relevant passages that answer the query\nQuery: "` | Qwen3 instruct prefix applied to all search queries via `embed_query()` |

---

## jsonl_to_md.py

**Purpose:** Convert Claude Code JSONL session files to readable Markdown. Extracts tool calls (input + output), task prompt, and final response. Optionally includes dispatch context from the main session (for subagent sessions).
**Input:** Path to a JSONL session file (Claude Code conversation log). Optional `--dispatch` flag to include the main session's dispatch context.
**Output:** Markdown file with tool call summary table, task prompt, final response, and per-tool-call detail sections.

**Usage:**
```bash
./venv/bin/python src/rag/jsonl_to_md.py \
    --input ~/.claude/projects/<project>/<session>.jsonl \
    --output /tmp/session.md

# Include dispatch context (for subagent sessions)
./venv/bin/python src/rag/jsonl_to_md.py \
    --input ~/.claude/projects/<project>/agents/<agent-id>.jsonl \
    --output /tmp/agent_session.md \
    --dispatch
```

**Output structure:**
- `# Dispatch Context` — pre/post-dispatch messages from main session (if `--dispatch`)
- `# Task Prompt` — first user message
- `# Tool Call Summary` — compact table: tool name, input brief, output size
- `# Final Response` — last assistant text block
- `# Tool Call N: ToolName` — full input + output for each tool call
