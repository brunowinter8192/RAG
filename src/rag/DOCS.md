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

**Purpose:** Generate embeddings using Qwen3-Embedding model.

**Input:** Text or list of texts
**Output:** List of embedding vectors (list[list[float]])

**Usage:**
```python
from src.rag.embedder import embed_workflow

embeddings = embed_workflow("Your text here")
embeddings = embed_workflow(["Text 1", "Text 2"], batch_size=16)
```

**Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| MODEL_NAME | gte-Qwen2-7B-instruct | HuggingFace model ID |

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

**Purpose:** Index documents into Qdrant vector database.

**Input:** Directory path, file patterns
**Output:** Number of indexed chunks

**Usage:**
```python
from src.rag.indexer import index_workflow

count = index_workflow("./docs", file_patterns=["*.md"])
count = index_workflow("./src", file_patterns=["*.py", "*.js"])
```

**Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| COLLECTION_NAME | documents | Qdrant collection name |
| VECTOR_SIZE | 4096 | Embedding dimension |
| QDRANT_PATH | ./qdrant_storage | Local Qdrant storage path |

---

## retriever.py

**Purpose:** Search indexed documents via vector similarity.

**Input:** Query string, number of results
**Output:** List of matching chunks with scores

**Usage:**
```python
from src.rag.retriever import search_workflow

results = search_workflow("How to configure authentication?", top_k=5)
```

**Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| COLLECTION_NAME | documents | Qdrant collection name |
| QDRANT_PATH | ./qdrant_storage | Local Qdrant storage path |
| DEFAULT_TOP_K | 5 | Default number of results |
