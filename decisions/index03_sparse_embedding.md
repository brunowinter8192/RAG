# Indexing Step 3: Sparse Embedding

## Status Quo

**Code:** `src/rag/sparse_embedder.py` (client), `src/rag/splade_server.py` (server)
**Model:** naver/splade-cocondenser-ensembledistil (SPLADE++) via sentence-transformers SparseEncoder
**Server:** FastAPI/uvicorn on port 8083 (single worker, synchronous)
**Dimensions:** 30522 (BERT vocabulary size, sparse)
**Storage:** pgvector `sparsevec(30522)` column

## Evidenz

### SearXNG Hybrid Sweep (30 queries, 2337 chunks)

| Retriever | NDCG@3 | NDCG@10 | Recall@10 |
|-----------|--------|---------|-----------|
| Dense (4096d) | 0.465 | 0.577 | 0.678 |
| Hybrid (RRF) | 0.298 | 0.474 | 0.656 |
| Sparse (SPLADE++) | 0.256 | 0.367 | 0.478 |

Sparse is 45% weaker than Dense. Hybrid is WORSE than Dense alone because SPLADE anti-correlates with correct relevance — its false positives displace Dense's correct results in RRF.

### Root Cause Analysis (dev/retrieval_eval/analysis/splade_findings.md)

1. **Domain mismatch:** SPLADE++ trained on MS-MARCO (web search). SearXNG corpus is YAML configs, Python API docs, code blocks — completely out-of-domain.
2. **Low activation:** Queries produce only 35-51 non-zero SPLADE dimensions (expected 100-300 on in-domain text).
3. **Subword artifacts:** Technical terms tokenize into ambiguous subwords:
   - "Valkey" → `val`(2.74) + `##key`
   - "Redis" → `red`(2.85) + `##is`
   - "SearXNG" → `sea`(2.44) + `##r` + `##x` + `##ng`
4. **Code chunks:** Zero lexical overlap with query tokens → SPLADE scores near 0 on correct targets.

### Qwen3 Paper Small Dataset (15 queries, 53 chunks)

| Retriever | NDCG@3 |
|-----------|--------|
| Sparse | 0.416 |
| Dense | 0.397 |
| Hybrid | 0.421 |

Sparse performed better on the small academic paper dataset — in-domain for MS-MARCO style text.

## Entscheidung

SPLADE++ kept as-is for now. Evidence shows it hurts more than it helps on technical docs. Decision deferred pending SPLADE v3 evaluation.

## Offene Fragen

- SPLADE v3 (naver/splade-v3): Better out-of-domain performance? Requires separate library (`pip install splade`), not sentence-transformers compatible.
- Should we drop Sparse entirely for technical docs? BM25 (already in pgvector via tsvector) might be sufficient.
- Domain-specific SPLADE fine-tuning: Is it worth the effort?
- SPLADE server async (Bead RAG-aoj): Single worker blocks concurrent requests. Not critical if Sparse is dropped.

## Quellen

- RAG Collection: SPLADE_v3_Paper (v3 training improvements, BEIR benchmarks)
- Anthropic contextual-retrieval (BM25 as sparse alternative)
- naver/splade GitHub repo (v3 model availability, custom model classes)
