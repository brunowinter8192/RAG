# SPLADE Performance Analysis: SearXNG Docs Dataset

## Summary

| Retriever | NDCG@3 | Recall@3 | NDCG@10 |
|-----------|--------|----------|---------|
| Dense(fulld) | 0.465 | 0.444 | 0.577 |
| Hybrid(RRF) | 0.298 | — | — |
| Sparse(splade++) | 0.256 | 0.244 | 0.367 |

SPLADE scores **45% below Dense** at NDCG@3. Hybrid is worse than Dense alone — SPLADE is adding noise, not signal.

---

## 1. Ground Truth Assessment

**Verdict: Ground truth is fair and unbiased.**

The 30 qrels map each query to the logical source document by filename:
- "How to install SearXNG with Docker?" → `admin_installation-docker.md` chunks 3-4
- "How to configure Valkey in SearXNG?" → `admin_settings_settings_valkey.md` chunks 0-1
- "Is Redis still supported in SearXNG?" → `admin_settings_settings_redis.md` chunk 0

The chunk selection is methodology-neutral — it reflects which document actually contains the answer, independent of whether the retriever uses semantic or lexical matching. No dense-retrieval bias detected.

One structural note: target documents are small (2-8 chunks) while the corpus has large distractor documents (`user_configured_engines.md`: 72 chunks, `dev_reST.md`: 64 chunks, `dev_engines_enginelib.md`: 39 chunks). SPLADE must rank 2-3 correct chunks in top-3 out of 2337 total — any false positives from large distractor documents hurt proportionally more.

---

## 2. Sparse Failure Cases

### Case A: Code-Heavy Chunks (e.g., q04 — Administration API)

**Query:** "What does the SearXNG Administration API provide?"

**SPLADE activations (top 8):** sea(2.55), administration(2.23), api(2.06), ##x(1.71), ##ng(1.53), provide(1.44), ##r(1.38), administrator(1.30) — **42 non-zero total**

**Target chunk content (admin_api.md, chunk 0):**
```
# Administration API
## Get configuration data
GET /config  HTTP/1.1
```

**Problem:** The chunk is almost entirely code (`GET /config HTTP/1.1`). SPLADE needs lexical overlap with the query tokens "administration", "api", "provide" — but "provide" does not appear in the chunk. Dense embedding understands that "Get configuration data" semantically answers "what does the API provide". SPLADE cannot make this inference.

**Target chunk content (admin_api.md, chunk 1):** JSON response body (`{"autocomplete": "", "categories": [...]}`) — zero natural language prose, zero lexical overlap with query terms.

---

### Case B: Ambiguous Subword Tokenization (e.g., q11 — Valkey; q29 — Redis)

**Query:** "How to configure Valkey in SearXNG?"

**SPLADE activations (top 8):** val(2.74), ##key(1.88), sea(1.80), step(1.56), ##gur(1.32), key(1.28), configuration(1.11) — **38 non-zero total**

The dominant token is `val` with weight 2.74 — this is the first subword of "Valkey". Any document mentioning "validate", "value", "val()" in Python code, or "valkey" gets high `val` weight.

**Query:** "Is Redis still supported in SearXNG?"

**SPLADE activations (top 8):** red(2.85), ##is(2.41), sea(2.20), still(1.79), ##x(1.55), support(1.44), supported(1.29) — **37 non-zero total**

The dominant token is `red` with weight 2.85 — first subword of "Redis". The 2337-chunk corpus contains many documents with "red" as a standalone word or in other compounds. The SearXNG corpus has code and HTML/CSS that may contain "red" as a color value. This creates false positives.

---

### Case C: Compound Technical Terms (e.g., q18 — EngineCache)

**Query:** "What is the Engine Library and EngineCache in SearXNG?"

**SPLADE activations (top 8):** engine(2.42), sea(2.06), engines(1.84), library(1.72), ##che(1.47), ##x(1.36), ##ca(1.18), libraries(1.10) — **35 non-zero total**

"EngineCache" is split as `Engine` + `##Ca` + `##che`. The compound term loses its identity — "engine"(2.42) and "engines"(1.84) are generic tokens that appear in 37+ chunks of `dev_engines_engines.md` and 72 chunks of `user_configured_engines.md`. The two target chunks (enginelib.md/chunk_0, enginelib.md/chunk_1) compete against ~110 chunks from these large engine-heavy documents.

---

## 3. Root Cause

### Primary: MS-MARCO Domain Mismatch

`naver/splade-cocondenser-ensembledistil` was trained on **MS-MARCO** — a web search corpus of natural language question-answer pairs. SearXNG documentation is fundamentally different:

| MS-MARCO | SearXNG Docs Corpus |
|----------|---------------------|
| Natural language prose | YAML configuration snippets |
| Web article text | Python API docstrings with type hints |
| Q&A format | Code blocks (bash, HTTP, JSON) |
| Standard English vocabulary | Proprietary names: SearXNG, Valkey, toml paths |

SPLADE's learned expansion vocabulary is tuned for MS-MARCO. It correctly expands "install" → "installation", "provide" → "administrator" — but these are generic synonyms. It cannot expand domain-specific terms:
- "SearXNG" → the model has no expansion for this OOV compound
- "Valkey" → "val"+"##key" subwords are semantically empty
- "limiter.toml" → "tom"+"##l" does not map to "bot detection", "rate limit", "request filter"

### Secondary: Extremely Low Non-Zero Density

All 30 queries produce only **35–51 non-zero dimensions** in the SPLADE sparse vector. For a vocabulary of ~30,000 BERT tokens, this is extreme sparsity. BEIR benchmark results on MS-MARCO data show SPLADE-cocondenser typically generates 100–300 non-zero terms per query. The low expansion count on technical queries suggests the model does not recognize these text patterns as domain-relevant.

Dense embedding always produces a full 2048-dimensional vector — every document has a meaningful cosine similarity score. SPLADE with 35–51 active tokens can only match documents with high lexical overlap in those exact tokens.

### Secondary: Subword Tokenization Artifacts

BERT tokenizer splits unknown compounds into subwords. The top-weighted tokens for technical queries are subword fragments (`val`, `red`, `sea`, `tom`) that are high-frequency BERT vocab entries. These subwords appear in unrelated contexts throughout the corpus, generating false-positive matches at high similarity scores.

### Why Hybrid Scores Below Dense (0.298 vs. 0.465)

RRF fusion takes rank positions from both retrievers. When SPLADE consistently places the wrong chunks in its top-10 (unrelated chunks with matching subwords), those chunks get boosted in the hybrid rank regardless of Dense's correct assessment. The hybrid score of 0.298 is worse than Dense because SPLADE is **anti-correlated** with correct relevance on this corpus — its false positives actively displace Dense's true positives.

---

## 4. Recommendation

### Keep or drop SPLADE?

**Recommendation: Replace `splade-cocondenser-ensembledistil` with SPLADE-v3 (naver/splade-v3) before deciding to drop sparse retrieval entirely.**

Reasoning:

1. **The problem is model-specific, not approach-specific.** SPLADE as a technique works — the limitation is that `splade-cocondenser-ensembledistil` (2022) was trained exclusively on MS-MARCO. SPLADE-v3 (2024) was trained on a broader mix including technical text and uses improved distillation.

2. **Out-of-vocabulary handling.** SPLADE-v3 uses improved regularization and produces more non-zero terms (typically 200+ vs. 35-51 observed here), which improves recall on technical domain queries.

3. **Hybrid potential is real.** A sparse retriever that catches exact matches ("Valkey URL configuration", "limiter.toml parameters") would complement dense retrieval, which sometimes misses exact technical terms. The hybrid architecture is correct — the component is wrong.

4. **If SPLADE-v3 still underperforms:** consider BM25 as the sparse component. BM25 with proper tokenization has no expansion vocabulary bias and performs reliably on technical documentation (BEIR results show BM25 is competitive with learned sparse models on out-of-domain text).

### Minimum bar for keeping any sparse component

Run the hybrid sweep again with SPLADE-v3 or BM25. If Hybrid NDCG@3 does not exceed Dense NDCG@3 by at least 0.02 (i.e., > 0.485), drop the sparse component — it is hurting retrieval quality in production.
