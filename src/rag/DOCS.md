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

**Environment Variables (.env):**
| Variable | Default | Description |
|----------|---------|-------------|
| EMBEDDING_URL | http://localhost:8081/v1/embeddings | llama.cpp server endpoint |
| EMBEDDING_MODEL | Qwen3-Embedding-8B | Model name for API |
| EMBEDDING_DIM | 4096 | Vector dimension |

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

### index_json_workflow (Recommended)

Index from pre-chunked chunks.json file.

**Input:** Path to chunks.json
**Output:** Number of indexed chunks

**Usage:**
```python
from src.rag.indexer import index_json_workflow

count = index_json_workflow("./data/documents/paper1/chunks.json")
```

**chunks.json format:**
```json
{
  "source_pdf": "/path/to/original.pdf",
  "created": "2025-12-28T...",
  "chunks": [
    {"index": 0, "content": "..."},
    {"index": 1, "content": "..."}
  ]
}
```

### index_workflow (Legacy)

Index from directory, re-chunking files.

**Input:** Directory path, file patterns
**Output:** Number of indexed chunks

**Usage:**
```python
from src.rag.indexer import index_workflow

count = index_workflow("./docs", file_patterns=["*.md"])
```

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
    content TEXT,
    source TEXT,
    chunk_index INTEGER,
    total_chunks INTEGER,
    embedding vector(4096)
)
```

---

## retriever.py

**Purpose:** Search indexed documents via vector cosine similarity.

**Input:** Query string, number of results
**Output:** List of matching chunks with scores

**Usage:**
```python
from src.rag.retriever import search_workflow

results = search_workflow("How to configure authentication?", top_k=5)
```

**Output Format:**
```python
[
    {
        "content": "The actual chunk text...",
        "source": "/path/to/file.pdf",
        "chunk_index": 0,
        "score": 0.8742  # cosine similarity (1 - distance)
    }
]
```

**Environment Variables:** Same as indexer.py (PostgreSQL connection)
