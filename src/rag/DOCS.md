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

**Input:** Directory path, file patterns
**Output:** Number of indexed chunks

**Usage:**
```python
from src.rag.indexer import index_workflow

count = index_workflow("./docs", file_patterns=["*.md"])
count = index_workflow("./src", file_patterns=["*.py", "*.js"])
```

**Environment Variables (.env):**
| Variable | Default | Description |
|----------|---------|-------------|
| PG_HOST | localhost | PostgreSQL host |
| PG_PORT | 5433 | PostgreSQL port |
| PG_USER | rag | Database user |
| PG_PASSWORD | rag | Database password |
| PG_DATABASE | rag | Database name |
| EMBEDDING_DIM | 4096 | Vector dimension |

**Schema:**
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
        "source": "/path/to/file.md",
        "chunk_index": 0,
        "score": 0.8742  # cosine similarity (1 - distance)
    }
]
```

**Environment Variables:** Same as indexer.py (PostgreSQL connection)
