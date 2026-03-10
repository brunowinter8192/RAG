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
```

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

---

## chunker.py

**Purpose:** Split documents into semantic chunks for embedding.

**Input:** File path, chunking strategy
**Output:** List of chunk dicts with content and metadata

**Usage:**
```python
from src.rag.chunker import chunk_workflow

chunks = chunk_workflow("docs/readme.md", strategy="semantic")
chunks = chunk_workflow("src/main.py", strategy="code")
```

**Strategies:**
| Strategy | Use Case |
|----------|----------|
| semantic | Markdown, text documents (sentence-aware recursive splitting) |
| code | Source code (function/class-level) |
| fixed | Fallback (fixed size with overlap) |

**Semantic Chunking (Recursive Split):**

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

**Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| DEFAULT_CHUNK_SIZE | 1000 | Max characters per chunk |
| DEFAULT_OVERLAP | 200 | Overlap between chunks (word-aligned)

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

**Auto-start:** If SPLADE server not running, starts it automatically via uvicorn subprocess (same pattern as embedder.py).

**Environment Variables (.env):**
| Variable | Default | Description |
|----------|---------|-------------|
| SPLADE_URL | http://localhost:8083/v1/sparse-embeddings | SPLADE server endpoint |

**Constants:**
| Constant | Value | Description |
|----------|-------|-------------|
| SPLADE_HEALTH_URL | http://localhost:8083/health | Health check endpoint |

---

## indexer.py

**Purpose:** Index documents into PostgreSQL with pgvector.

### index_json_workflow

Index from pre-chunked chunks.json file.

**Input:** Path to chunks.json
**Output:** Number of indexed chunks

**Behavior:**
- Deletes existing chunks for same collection before inserting (no duplicates)
- Processes in batches (BATCH_SIZE = 32)
- Token truncation handled by embedder.py

**Usage:**
```python
from src.rag.indexer import index_json_workflow

count = index_json_workflow("./data/documents/specification/chunks.json")
```

**chunks.json format:**
```json
{
  "source": "data/documents/specification/specification.md",
  "document": "specification.md",
  "created": "2025-12-31T...",
  "chunks": [
    {"index": 0, "content": "..."},
    {"index": 1, "content": "..."}
  ]
}
```

**Metadata Extraction:**
- `collection` = parent folder name (e.g., "specification")
- `document` = from chunks.json "document" field or fallback to stem + ".md"

### backfill_splade_workflow

Backfill SPLADE sparse embeddings for chunks that have NULL `sparse_embedding`. Only computes sparse vectors — does NOT re-embed dense vectors.

```python
from src.rag.indexer import backfill_splade_workflow

count = backfill_splade_workflow("GraphQL_GH")
```

**CLI Usage (via workflow.py):**
```bash
./venv/bin/python workflow.py backfill-splade --collection GraphQL_GH
```

**When to use:** After adding the `sparse_embedding` column or when new chunks were indexed without SPLADE (e.g., embedding server was down). Much faster than full re-index because it skips dense embedding computation.

### delete_collection

Delete all chunks for a given collection (used internally for re-indexing).

```python
from src.rag.indexer import delete_collection
deleted = delete_collection(conn, "specification")
```

### delete_workflow

Delete chunks by collection and/or document (CLI interface).

```python
from src.rag.indexer import delete_workflow

# Delete entire collection
deleted = delete_workflow(collection="specification")

# Delete specific document
deleted = delete_workflow(document="chapter1.md")

# Delete specific document in collection
deleted = delete_workflow(collection="specification", document="specification.md")
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| collection | str | None | Filter by collection name |
| document | str | None | Filter by document name |

At least one of `collection` or `document` is required.

### Environment Variables (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| POSTGRES_HOST | localhost | PostgreSQL host |
| POSTGRES_PORT | 5432 | PostgreSQL port |
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
    sparse_embedding sparsevec(30522)
)
```

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

**Model:** Qwen3-Reranker-0.6B (GGUF Q8_0, ~610MB). Official ggml-org conversion.

**Server:** Second llama-server instance on port 8082 with `--rerank -c 32768` flags. Auto-started on first use (same pattern as embedder.py). Context size 32768 required to handle reranking payloads.

**Environment Variables (.env):**
| Variable | Default | Description |
|----------|---------|-------------|
| RERANKER_URL | http://localhost:8082/v1/rerank | llama.cpp reranker endpoint |

**Constants:**
| Constant | Value | Description |
|----------|-------|-------------|
| RERANKER_HEALTH_URL | http://localhost:8082/health | Health check endpoint |
| RERANKER_MODEL_PATH | models/qwen3-reranker-0.6b-q8_0.gguf | Model file path |

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
| RERANK_CANDIDATES | 10 | Number of RRF candidates sent to cross-encoder (limited by llama-server context) |
| RRF_K | 60 | RRF smoothing constant |

### list_collections_workflow

List all indexed collections with chunk counts.

```python
from src.rag.retriever import list_collections_workflow

results = list_collections_workflow()
# [{"collection": "specification", "chunks": 402}]
```

### list_documents_workflow

List all documents in a collection with chunk counts.

```python
from src.rag.retriever import list_documents_workflow

results = list_documents_workflow("specification")
# [{"document": "specification.md", "chunks": 402}]
```

### read_document_workflow

Read continuous text from a document starting at a specific chunk.

```python
from src.rag.retriever import read_document_workflow

result = read_document_workflow("specification", "specification.md", start_chunk=50, num_chunks=10)
# {
#     "content": "...",
#     "collection": "specification",
#     "document": "specification.md",
#     "start_chunk": 50,
#     "num_chunks": 10
# }
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| collection | str | required | Collection name |
| document | str | required | Document name |
| start_chunk | int | required | Chunk index to start reading from |
| num_chunks | int | 5 | Number of chunks to read (max 20) |

### Helper Functions

**merge_chunks(chunks):** Merge chunks with overlap deduplication. Finds common suffix/prefix between adjacent chunks and removes duplicates.

**find_overlap(text1, text2, max_overlap=300):** Find the longest suffix of text1 that matches prefix of text2. Returns overlap size in characters.

### search_hybrid_workflow

Hybrid search combining vector similarity and SPLADE sparse search with Reciprocal Rank Fusion (RRF). Optional cross-encoder reranking for higher precision.

```python
from src.rag.retriever import search_hybrid_workflow

# Best default for large collections
results = search_hybrid_workflow("authentication patterns", collection="docs")

# With context expansion
results = search_hybrid_workflow("TPC-H benchmark", top_k=10, collection="specification", neighbors=1)

# With cross-encoder reranking for maximum precision
results = search_hybrid_workflow("complex query", top_k=5, collection="docs", rerank=True)
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| query | str | required | Search query (natural language or keywords) |
| top_k | int | 5 | Number of results (max 20) |
| collection | str | None | Filter by collection name |
| document | str | None | Filter by document name |
| neighbors | int | 0 | Include N chunks before/after each match (0-2) |
| rerank | bool | True | Re-score with cross-encoder (Qwen3-Reranker-0.6B) |

**How it works:**
1. Runs vector search (top 50 candidates) and SPLADE sparse search (top 50 candidates)
2. Applies RRF fusion: `score = Σ 1/(k + rank)` across both result lists (k=60)
3. Chunks appearing in both lists get boosted scores
4. If `rerank=False`: Returns top_k results sorted by fused score
5. If `rerank=True` (default): Top 10 RRF candidates (RERANK_CANDIDATES) sent to cross-encoder, returns top_k by relevance score. Results below 0.3 cross-encoder score are filtered out.

**SPLADE vs BM25:** SPLADE (used in hybrid) learns term importance and expands synonyms automatically (e.g., "revenue" matches "profit", "earnings"). BM25 (used in `search_keyword_workflow`) matches exact terms only. Hybrid combines dense semantic + SPLADE sparse for best coverage.

**When to use:** Default choice for large collections (100+ documents). Use `search_workflow` for pure semantic queries, `search_keyword_workflow` for exact term matching. Reranking is ON by default; use `rerank=False` for faster but less precise results.

### splade_search

SPLADE sparse vector search using `sparse_embedding <=> query::sparsevec` cosine distance.

```python
# Called internally by search_hybrid_workflow — not typically used directly
from src.rag.retriever import splade_search
results = splade_search(conn, "revenue growth", top_k=50, collection="docs")
```

**How it works:**
1. Generates sparse query vector via `sparse_embed_workflow(query)`
2. Formats as pgvector sparsevec string: `{idx1:val1,idx2:val2}/30522`
3. Queries `sparse_embedding <=> query::sparsevec` for cosine distance
4. Returns same dict structure as `search_vectors()` and `bm25_search()`

### search_keyword_workflow

BM25 keyword search using PostgreSQL full-text search (tsvector).

```python
from src.rag.retriever import search_keyword_workflow

# Search for exact terms
results = search_keyword_workflow("l_suppkey", collection="specification")

# Multiple keywords (AND logic)
results = search_keyword_workflow("TPC-H benchmark", top_k=10)
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| query | str | required | Keywords to search for (space = AND) |
| top_k | int | 5 | Number of results (max 20) |
| collection | str | None | Filter by collection name |
| document | str | None | Filter by document name |

**When to use:**
- Exact term matches ("l_suppkey", "TPC-H")
- Finding definitions
- Technical terms, column names
- Specific phrases

**Complements search_workflow:** Use `search()` for semantic/conceptual queries, `search_keyword()` for exact matches.
