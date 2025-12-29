# Bug: llama.cpp Embedding Server Crash

**Datum:** 2025-12-29
**Status:** Fixed

## Symptom

llama.cpp Server crasht nach 1-2 Embedding Requests während Indexierung.

```
httpx.RemoteProtocolError: Server disconnected without sending a response.
Indexed 1/413 chunks
```

Server Log zeigt:
- Request 1 (285 tokens): OK
- Request 2 (640 tokens): Server stirbt ohne Response

## Root Cause

**llama.cpp Assertion:**
```
GGML_ASSERT(cparams.n_ubatch >= n_tokens && "non-causal attention requires n_ubatch >= n_tokens")
```

Bei Embeddings verwendet llama.cpp **non-causal attention**. Diese erfordert, dass `n_ubatch` (micro-batch size) >= Anzahl Tokens im Request ist.

**Default Verhalten:**
```
main: setting n_batch = n_ubatch = 512
```

**Problem:**
- Chunk 1: 285 tokens < 512 → OK
- Chunk 2: 640 tokens > 512 → CRASH

## Fix

`start.sh` angepasst:

```bash
./llama.cpp/build/bin/llama-server \
  -m ./models/Qwen3-Embedding-8B-Q5_K_M.gguf \
  --embedding \
  --host 0.0.0.0 \
  --port 8081 \
  -ub 4096 \
  -b 4096
```

`-ub 4096` stellt sicher, dass auch größere Chunks (bis 4096 tokens) verarbeitet werden können.

## Token-basiertes Limit

Zusätzlich wurde ein token-basiertes Limit in `embedder.py` implementiert:

```python
MAX_TOKENS = 4000

def count_tokens(text: str) -> int:
    # Nutzt llama.cpp /tokenize endpoint
    response = httpx.post(TOKENIZE_URL, json={"content": text})
    return len(response.json()["tokens"])

def truncate_to_tokens(text: str, max_tokens: int) -> str:
    # Trunciert auf max_tokens falls nötig
    ...
```

Dies ersetzt das vorherige char-basierte Limit (MAX_CHUNK_CHARS=2000) im indexer.

## Discovery Process

1. **Symptom:** Server crasht nach 1-2 Embedding Requests
2. **Server Logs analysiert:** Task 1 (285 tokens) OK, Task 2 (640 tokens) crash
3. **Web Search:** `llama.cpp server crash embedding request`
4. **GitHub Issue gefunden:** [#12836](https://github.com/ggml-org/llama.cpp/issues/12836)
5. **Root Cause identifiziert:** `n_ubatch >= n_tokens` Assertion für non-causal attention

**Key Insight:** Server Logs zeigten Token-Counts, die den ubatch-Default (512) überschritten.

## Referenzen

- [GitHub Issue #12836](https://github.com/ggml-org/llama.cpp/issues/12836) - Ursprünglicher Bug Report
- [GitHub PR #17912](https://github.com/ggml-org/llama.cpp/pull/17912) - Fix in llama.cpp (merged 2 Wochen vor diesem Bug)

## Zusätzliche Fixes in dieser Session

1. **Duplikate Prevention:** `delete_source()` vor INSERT hinzugefügt (indexer.py)
2. **Legacy Code Removal:** `index_workflow()` entfernt
3. **README Updates:** `/pdf-convert`, Prerequisites Section
