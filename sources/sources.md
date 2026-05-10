# Sources

**RAG Collection `RAG_reference`** — searchable via `rag-cli search_hybrid <query> RAG_reference`.
**GitHub / Reddit** — accessible via `github-search` / `agent-reddit-search` skills (not in local index).

Organized per decision file. Decision files without external sources (architectural / code-level only) are listed at the bottom for completeness.

---

## index01 — Chunking

### Indexed
- **Pipeline_Optimization** — arxiv 2511.22240 (also covers retrieval03, retrieval04)
- **Rethinking_Chunk_Size_Long_Document** — arxiv 2505.21700

### Reddit
- r/Rag — Chunking for Decoder Models (10 threads)

---

## index02 — Dense Embedding

### Indexed
- **Qwen3_Embedding** — arxiv 2506.05176 (also covers retrieval01)

### GitHub
- `QwenLM/Qwen3-Embedding` — Model Card + Eval Code (also covers retrieval04)

### Reddit
- Embedding Model SOTA (15 threads)

---

## index03 — Sparse Embedding (SPLADE)

### Indexed
- **SPLADE_v3** — arxiv 2403.06789

---

## index04 — Storage (pgvector)

### GitHub
- `pgvector/pgvector` — Releases & roadmap

### Reddit
- pgvector SOTA Discussion (14 threads)

---

## retrieval01 — Query Embedding

### Indexed
- **Qwen3_Embedding** — see index02

---

## retrieval03 — Fusion

### Indexed
- **Pipeline_Optimization** — see index01
- **Fusion_Functions_Hybrid_Retrieval** — dl.acm 10.1145/3596512

---

## retrieval04 — Reranking

### Indexed
- **Pipeline_Optimization** — see index01

### GitHub
- `QwenLM/Qwen3-Embedding` — see index02 (Reranker model card)

### Reddit
- r/Rag — Reranker Threshold Calibration

---

## eval01 — Methodology

### Indexed
- **RAGAS_Evaluation_Framework** — RAG_reference collection
- **RAG_Evaluation_Survey_2025** — RAG_reference collection
- **Pipeline_Optimization** — arxiv 2511.22240 (see index01)
- **Fusion_Functions_Hybrid_Retrieval** — dl.acm 10.1145/3596512 (see retrieval03)

---

## Decisions Without External Sources

retrieval02 (Search primitives), delivery01 (MCP tools), box_architecture, infra01 (Connection management), infra02 (Lock and status), OldThemes — code-level / architectural decisions, no external research consulted.
