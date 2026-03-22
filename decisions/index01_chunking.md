# Indexing Step 1: Chunking

## Status Quo (IST)

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

### Rethinking Chunk Size (RAG: Rethinking_Chunk_Size_Long_Document_Retrieval)

Systematic evaluation of fixed-size chunking across 6 datasets with 2 embedding models (Stella = Decoder/Qwen2-basis, Snowflake = Encoder). Chunk sizes: 64-1024 tokens.

| Model Type | Optimal Chunk Size | Datasets |
|-----------|-------------------|----------|
| Decoder (Stella, Qwen2-basis, 130k ctx) | 512-1024 tokens | NarrativeQA, NQ, TechQA |
| Encoder (Snowflake, 8k ctx) | 64-128 tokens | SQuAD, CovidQA |

**Key finding:** Chunk-size sensitivity is model-dependent. Decoder models benefit from larger chunks (+5-8% Recall@1 vs Encoder at 512-1024 tokens). Encoder models prefer smaller chunks for entity-based matching.

### Beyond Chunk-Then-Embed Taxonomy (RAG: Beyond_Chunk_Then_Embed_Taxonomy)

Comprehensive evaluation of chunking strategies across 4 Encoder models (Jina-v2, Jina-v3, Nomic, E5-large) on BEIR datasets.

**Key finding:** For in-corpus retrieval, structure-based methods (paragraph, fixed-size) outperform LLM-guided and semantic methods. Difference between structure-based methods is only 1-3%. Paragraph-based slightly best for 3/4 models.

### Chunking Eval (dev/indexing/chunking_eval/)

5-Doc subset sweep on RAG_MCP: 6 variants (A-F, 500-1500 chars). **Result: all variants Recall@3/5/10 = 1.000.** Corpus too small to discriminate — needs larger benchmark dataset.

### Qwen3 vs BGE-M3 (RAG: medium.com__mrAryanKumar)

Anecdotal: "strong performance with chunk sizes of 2,000–4,000 tokens" for Qwen3. No methodology provided.

## Recommendation (SOLL)

Pending — external evidence suggests current 1000 chars (~250 tokens) may be suboptimal for Decoder-based Qwen3-8B. Stella (same Qwen2 architecture family) optimal at 512-1024 tokens (~2000-4000 chars). Own benchmark on Qwen3-8B with realistic corpus needed before setting concrete SOLL (Bead RAG-sfd).

## Offene Fragen

- Optimal chunk size for Qwen3-Embedding-8B specifically — no published benchmark exists
- Benchmark dataset needed: own RAG_MCP too small, MS-MARCO subset or synthetic dataset?
- Chunk size × MRL dimension interaction — does 1024d change the optimal chunk size vs 4096d?
- Henne-Ei: Chunk-size optimal for current config, but config may change after full pipeline eval
- Structure-based (paragraph) vs fixed-size: "Beyond" paper shows paragraph slightly better — worth testing?

## Quellen

- RAG Collection: Pipeline_Optimization_Paper (Chunks 6, 20, 28, 29, 36) — GTE-large, Encoder
- RAG Collection: Rethinking_Chunk_Size_Long_Document_Retrieval — Stella/Snowflake, Decoder vs Encoder
- RAG Collection: Beyond_Chunk_Then_Embed_Taxonomy — Jina/Nomic/E5, BEIR datasets
- RAG Collection: medium.com__mrAryanKumar (Qwen3 vs BGE-M3 comparison)
- RAG Collection: medium.com__yashasvimantha (MRL Sweet Spot Qwen3-0.6B)
- RAG Collection: research_trychroma_com__evaluating-chunking (Chroma Technical Report)
- Anthropic contextual-retrieval (Contextual Chunking concept)
- Late Chunking vs Contextual Retrieval comparison
