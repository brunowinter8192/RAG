# NULL Embeddings from llama-server

## Problem

llama-server returns `200 OK` but embedding vectors contain all `NULL` values (4096 x NULL). A single such request corrupts the server state permanently — all subsequent requests return NULLs until restart.

```
Embedding dim: 4096
NULL values: 4096
First 10 values: [None, None, None, None, ...]
```

## Root Cause

**Content-specific tokenizer issue with Qwen3-Embedding-8B.** Text that begins directly with a Python `import` token (no preceding context) produces NULL vectors.

Affected pattern: Chunks where the chunker splits a Markdown code block, leaving the chunk starting with naked `import X` statements.

Reproduction (2026-03-05, Agent af3e9ee576f6b7723, 150 chunks):
- 3 of 150 chunks (2%) produce NULLs
- Chunk 16: `import BFSDeepCrawlStrategy\nfrom crawl4ai...`
- Chunk 73: `import AsyncGenerator, Optional, Set, List, Dict`
- Chunk 92: `import ContentScrapingStrategy, LXMLWebScrapingStrategy`
- All start with naked `import` — no Markdown wrapper, no prose prefix

## Previous Diagnoses (ALL WRONG)

| Hypothesis | Status | Evidence |
|------------|--------|---------|
| Whitespace bloat in chunks | WRONG | Whitespace ratio 1.04-1.22, well below threshold |
| Batch size >16 triggers NULLs | WRONG | Occurs on single requests with fresh server |
| Cumulative server state after many requests | WRONG | First request with bad content triggers it |
| Server params (-ub, -b, -np) fix it | WRONG | Tested 512, 8192, 16384 — all fail on same content |
| llama.cpp version bug | WRONG | Persists on b7564 and b8198 (latest) |

## Fix

**Prefix every chunk with `search_document: ` before sending to embedding server.**

This is the Qwen3-Embedding model card's recommended prefix for document retrieval. It prevents the tokenizer from misinterpreting naked code as input.

Verified: All 3 NULL chunks produce valid embeddings with prefix. Server remains stable.

```python
# In embedder.py or indexer.py before calling embed API
PREFIX = "search_document: "
texts = [PREFIX + t for t in texts]
```

**Safety net:** Additionally validate embeddings before DB insert. Skip chunks with NULL vectors and log a warning.

## GitHub References

- ggml-org/llama.cpp#14812: Similar symptom (NULLs after extended operation), different trigger. Workaround: reduce -ub to 512.
- ggml-org/llama.cpp#12836: Crash when -b > -ub with embeddings (non-causal attention constraint). Fixed in PR #17912.
- QwenLM/Qwen3-Embedding#122: PAD vs EOS token discrepancy in tokenizer config.
- No exact match for our content-specific NULL trigger found on GitHub.

## Setup

- Model: Qwen3-Embedding-8B-Q8_0.gguf
- Server: llama.cpp llama-server (tested b7564 and b8198)
- Platform: macOS M4 Pro, Metal GPU
- Server params: -ngl 99 (full GPU offload)
