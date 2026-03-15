# Indexing Step 1: Chunking

## Status Quo

**Code:** `src/rag/chunker.py` (Plugin: `workflow.py chunk`)
**Method:** Recursive character split with hierarchical separators
**Separators:** `\n\n` → `\n` → `. ` → `! ` → `? ` → ` `
**Config:** 1000 chars target, 200 chars overlap (word-aligned)
**CLI:** `./venv/bin/python workflow.py chunk --input file.md --chunk-size 1000 --overlap 200`

No markdown-awareness (headers not treated as boundaries). No content-adaptive splitting (code, prose, tables treated identically).

## Evidenz

### Pipeline Optimization Paper (RAG: Pipeline_Optimization_Paper)

| Chunk Size | Acc@3 | NDCG@3 |
|-----------|-------|--------|
| 2000 chars | 0.412 | 0.356 |
| 512 chars | 0.460 | 0.415 |
| Semantic (variable) | 0.456 | 0.404 |

512 chars outperforms 2000 chars by +5pp Acc@3. Semantic chunking performs comparably to 512 fixed. Adding a reranker bridges ~50% of the gap between 2000 and 512.

### Our Chunk Statistics (all collections)

- 5553 chunks total, avg 843 chars, median 889 chars, max 1190 chars
- p90: 990, p95: 1005, p99: 1138

### Chunking Eval Plan (dev/retrieval_eval/analysis/chunking_evaluation_plan.md)

6 variants planned but not yet executed:
- A: 500 chars, 100 overlap
- B: 750 chars, 150 overlap
- C: 1000 chars, 200 overlap (current baseline)
- D: 1500 chars, 300 overlap
- E: Markdown-header-aware (split at ## boundaries)
- F: Semantic sentence-level (nltk)

## Entscheidung

1000 chars was chosen as initial default without benchmarking. No formal evaluation against alternatives on our data.

## Offene Fragen

- Is 1000 chars optimal for our use case (technical docs, API refs, papers)?
- Would markdown-header-aware splitting improve retrieval for structured docs?
- Does chunk size interact with MRL dimension reduction (smaller dims → smaller chunks better)?
- Paper evidence suggests 512 chars is better — does this hold on our data?

## Quellen

- RAG Collection: Pipeline_Optimization_Paper (Chunks 6, 20, 28, 29, 36)
- NVIDIA chunking-strategy benchmark
- Chroma evaluating-chunking research
- Superlinked chunking-methods (SentenceSplitter > SemanticSplitter finding)
- Anthropic contextual-retrieval (Contextual Chunking concept)
- Late Chunking vs Contextual Retrieval comparison
