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
| `retrieve_dense` | `(query, collection, top_k=10) -> list[dict]` | Embed query (instruct prefix), cosine search |
| `retrieve_sparse` | `(query, collection, top_k=10) -> list[dict]` | SPLADE-embed query, sparse cosine search |
| `retrieve_hybrid` | `(query, collection, top_k=10, rrf_k=60) -> list[dict]` | Dense + sparse search, RRF fusion |
| `retrieve_cc` | `(query, collection, top_k=10, alpha=0.7) -> list[dict]` | Dense + sparse search, Convex Combination fusion |
| `retrieve_cc_rerank` | `(query, collection, top_k=10, alpha=0.7, rerank_candidates=50) -> list[dict]` | CC fusion then cross-encoder rerank |
| `rerank` | `(query, results, top_k=10) -> list[dict]` | Cross-encoder rerank via llama-server port 8082 |

**Dense query prefix:** `Instruct: Given a search query, retrieve relevant passages that answer the query\nQuery: `

**Candidates fetched before top_k cutoff:** 50

---

## Analysis Scripts

### A_retrieval_eval.py

**Purpose:** Evaluate retrieval quality against ground truth documents and snippets. Produces per-mode reports with document and snippet recall metrics. Sweep mode runs all fusion parameter combinations in one pass.

**Prerequisites:** Embedding server (8081) always. SPLADE (8083) for sparse, hybrid, cc, cc+rerank, hybrid+rerank modes. Reranker (8082) for any mode containing "rerank".

**CLI flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--collection` | `RAG_MCP` | Collection name to query |
| `--queries` | `dev/retrieval/queries_rag_mcp.json` | Queries JSON path |
| `--top-k` | `10` | Results per query |
| `--modes` | `dense` | Comma-separated modes |
| `--alpha` | `0.7` | CC fusion alpha weight for dense (used when mode is `cc`) |
| `--rrf-k` | `60` | RRF K constant (used when mode is `hybrid`) |
| `--sweep` | flag | Run full parameter sweep — ignores `--modes` |

**Valid modes:** `dense`, `sparse`, `hybrid`, `cc`, `cc+rerank`, `hybrid+rerank`

**Queries JSON format:**
```json
{
  "queries": [
    {
      "query": "What embedding dimensions does Qwen3 support?",
      "type": "factual",
      "expected_documents": ["Qwen3_Embedding_Paper"],
      "expected_snippets": ["Matryoshka Representation Learning"]
    }
  ]
}
```

**Output:**
- `A_retrieval_eval_reports/eval_<mode>_<timestamp>.md` — per-mode report with per-query results and summary
- `A_retrieval_eval_reports/sweep_comparison_<timestamp>.md` — comparison table across all configs (only with `--sweep`)

**Usage:**
```bash
./venv/bin/python dev/retrieval/A_retrieval_eval.py \
    --collection RAG_MCP \
    --queries dev/retrieval/queries_rag_mcp.json \
    --modes dense,hybrid,cc

./venv/bin/python dev/retrieval/A_retrieval_eval.py \
    --modes cc --alpha 0.8

./venv/bin/python dev/retrieval/A_retrieval_eval.py --sweep
```

---

### A_retrieval_sandbox.py

**Purpose:** Explore retrieval results interactively across modes for a set of ad-hoc queries. No ground truth — outputs raw ranked results per query per mode for manual inspection.

**Prerequisites:** Embedding server (8081) always. SPLADE (8083) for sparse, hybrid, cc, cc+rerank, hybrid+rerank modes. Reranker (8082) for any mode containing "rerank".

**CLI flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--collection` | required | Collection name to query |
| `--queries` | required | Path to JSON file with queries list |
| `--top-k` | `5` | Results per query per mode |
| `--modes` | `dense,sparse,hybrid,cc` | Comma-separated modes |

**Valid modes:** `dense`, `sparse`, `hybrid`, `hybrid+rerank`, `cc`, `cc+rerank`

**Queries JSON format:**
```json
["What embedding dimensions does Qwen3 support?", "How does SPLADE work?"]
```

**Output:** `A_retrieval_sandbox_reports/retrieval_<collection>_<timestamp>.md`
- Per query, per mode: rank/score/document/chunk index with content snippet

**Usage:**
```bash
./venv/bin/python dev/retrieval/A_retrieval_sandbox.py \
    --collection RAG_MCP \
    --queries dev/retrieval/queries.json \
    --top-k 5

./venv/bin/python dev/retrieval/A_retrieval_sandbox.py \
    --collection RAG_MCP \
    --queries dev/retrieval/queries.json \
    --modes dense,hybrid,cc

./venv/bin/python dev/retrieval/A_retrieval_sandbox.py \
    --collection RAG_MCP \
    --queries dev/retrieval/queries.json \
    --modes cc+rerank \
    --top-k 10
```

---

### A_mrl_sweep.py

**Purpose:** Sweep embedding dimensions [256, 512, 768, 1024, 2048, 4096] to evaluate dense and hybrid retrieval quality across MRL truncation levels. Collection and dimensions are hardcoded (`COLLECTION = "RAG_MCP"`, `DIMENSIONS = [256, 512, 768, 1024, 2048, 4096]`). Requires full 4096d embeddings already indexed.

**Prerequisites:** Embedding server (8081), SPLADE (8083).

**Output:** `A_mrl_sweep_reports/mrl_sweep_<timestamp>.md`

**Usage:**
```bash
./venv/bin/python dev/retrieval/A_mrl_sweep.py
```

---

## Data Files

### queries_rag_mcp.json

20 queries (8 factual, 7 conceptual, 5 cross-document) with ground truth for the RAG_MCP collection. Used by `A_retrieval_eval.py`. Format: JSON object with `"queries"` array, each entry has `query`, `type`, `expected_documents`, `expected_snippets`.

---

### Current Test Database State

rag_test enthält RAG_MCP (28 Docs / 483 Chunks aus data/documents/RAG_MCP/, 1:1 mit Disk gespiegelt). Production-DB rag enthält wise2627 (3246 Chunks, alte Pipeline-Konfig 1000/200 + 4096d + SPLADE++). Fünf weitere Disk-Collections (searxng, FAUWingMaster, GoetheBWLMaster, linkedin, TradBot) sind nirgends indexiert.

### Query Coverage

20 Queries verweisen auf 24 unique Dokumente, alle 24 sind in rag_test.RAG_MCP vorhanden (kein Drift). 4 indexierte Dokumente werden von keiner Query getestet — anthropic__docs__en__build-with-claude__embeddings.md, docs_haystack_deepset_ai__docs__advanced-rag-techniques.md, docs_together_ai__docs__building-a-rag-workflow.md, docs_together_ai__docs__embeddings-rag.md. Mögliche Distraktoren oder Coverage-Lücke.

### Pipeline Coverage / Friction Boundary

Was die Eval heute prüft: alle Retrieval-Knöpfe ohne Re-Indexing-Bedarf — Modi (dense/sparse/hybrid/cc/cc+rerank/hybrid+rerank), Fusion-Parameter (RRF K, CC α), MRL-Dimension via separates Script.

Was die Eval nicht prüft trotz No-Re-Index-Möglichkeit: BM25/keyword (Code in src/rag/search_primitives.py vorhanden, nicht in p1_retriever.py exposed), top_k-Variation, score_threshold, query_prefix-Ablation.

Was die Eval nicht prüft weil Re-Index nötig: Chunking-Config, Dense-Embedding-Modell, Sparse-Embedding-Modell, Schema-Änderungen.

Wichtig: Eval läuft auf RAG_MCP, Production läuft auf wise2627 — die Eval-Aussagen (CC α=0.8 optimal, Reranker schadet auf technischen Docs) basieren auf RAG_MCP-Inhalten und generalisieren nicht zwingend.
