# dev/retrieval/ — Retrieval Pipeline Dev Suite

Self-contained modules and scripts for retrieval experiments. Imports pipeline modules from `dev/indexing/` (added to `sys.path` automatically).

All scripts run from project root:
```bash
./venv/bin/python dev/retrieval/<script>.py [args]
```

---

## Pipeline Modules

### p1_retriever.py

Imports `p2_embedder`, `p3_sparse_embedder`, `p4_db` from `dev/indexing/` via `sys.path` insert.

| Function | Signature | Description |
|----------|-----------|-------------|
| `retrieve_dense` | `(query, collection, top_k=10) -> list[dict]` | Embed query (instruct prefix + MRL 1024d), cosine search |
| `retrieve_sparse` | `(query, collection, top_k=10) -> list[dict]` | SPLADE-embed query, sparse cosine search |
| `retrieve_hybrid` | `(query, collection, top_k=10, rrf_k=60) -> list[dict]` | Dense + sparse search, RRF fusion |
| `rerank` | `(query, results, top_k=10) -> list[dict]` | Cross-encoder rerank via llama-server port 8082 |

**Dense query prefix:** `Instruct: Given a search query, retrieve relevant passages that answer the query\nQuery: `

**Candidates fetched before top_k cutoff:** 50

---

## A_retrieval_sandbox.py

**Purpose:** Test retrieval quality across modes for a set of queries.

**Prerequisites:** Embedding (8081) + SPLADE (8083) for all modes. Reranker (8082) for `hybrid+rerank` only.

**CLI flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--collection` | required | Collection name to query |
| `--queries` | required | Path to JSON file with queries list |
| `--top-k` | 5 | Results per query per mode |
| `--modes` | `dense,sparse,hybrid,hybrid+rerank` | Comma-separated modes |

**Valid modes:** `dense`, `sparse`, `hybrid`, `hybrid+rerank`

**Queries JSON format:**
```json
["What embedding dimensions does Qwen3 support?", "How does SPLADE work?"]
```

**Output:** `A_retrieval_sandbox_reports/retrieval_<collection>_<timestamp>.md`
- Per query, per mode: rank/score/document/snippet table (300 char snippets)

**Usage:**
```bash
./venv/bin/python dev/retrieval/A_retrieval_sandbox.py \
    --collection RAG_MCP \
    --queries dev/retrieval/queries.json \
    --top-k 5

./venv/bin/python dev/retrieval/A_retrieval_sandbox.py \
    --collection RAG_MCP \
    --queries dev/retrieval/queries.json \
    --modes dense,hybrid

./venv/bin/python dev/retrieval/A_retrieval_sandbox.py \
    --collection RAG_MCP \
    --queries dev/retrieval/queries.json \
    --modes hybrid+rerank \
    --top-k 10
```
