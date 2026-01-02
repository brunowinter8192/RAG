# src/rag/ - RAG Pipeline Modules

## Working Directory

```
cd /path/to/MCP/RAG
```

## Directory Structure

```
src/rag/
├── __init__.py
├── embedder.py
├── chunker.py
├── indexer.py
├── retriever.py
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
| semantic | Markdown, text documents (paragraph-aware) |
| code | Source code (function/class-level) |
| fixed | Fallback (fixed size with overlap) |

**Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| DEFAULT_CHUNK_SIZE | 1000 | Max characters per chunk |
| DEFAULT_OVERLAP | 200 | Overlap between chunks |

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
    embedding vector(4096)
)
```

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
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| query | str | required | Search query |
| top_k | int | 5 | Number of results (max 20) |
| collection | str | None | Filter by collection name |
| document | str | None | Filter by document name |

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

**Environment Variables:** Same as indexer.py (PostgreSQL connection)

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
