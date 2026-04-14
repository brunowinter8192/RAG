---
name: agent-rag-search
description: RAG CLI tool reference for search agents. Invoke via bash using cli.py. Use when performing semantic search, hybrid search, keyword search, reading documents, listing collections, or listing documents in the RAG vector database.
---

# RAG CLI Tools — Reference

## CLI Invocation

All tools are invoked via the Bash tool using absolute paths:

```bash
/Users/brunowinter2000/Documents/ai/Meta/ClaudeCode/MCP/RAG/venv/bin/python \
  /Users/brunowinter2000/Documents/ai/Meta/ClaudeCode/MCP/RAG/cli.py <cmd> [args]
```

### Quick Reference — All 6 Tools

```bash
# Discovery
python cli.py list_collections
python cli.py list_documents my_collection
python cli.py list_documents my_collection --document "arxiv_%"

# Search
python cli.py search_hybrid "transformer attention mechanism" my_collection --top-k 20
python cli.py search_hybrid "cost function" my_collection --document "paper.md" --neighbors 1
python cli.py search_hybrid "query" my_collection --no-rerank   # faster, lower precision

python cli.py search "semantic similarity" my_collection --top-k 30 --neighbors 2
python cli.py search_keyword "learning_rate dropout" my_collection --top-k 20

# Read
python cli.py read_document my_collection paper.md 42
python cli.py read_document my_collection paper.md 40 --num-chunks 15
```

**Always use full absolute paths** when invoking from the Bash tool:

```bash
/Users/brunowinter2000/Documents/ai/Meta/ClaudeCode/MCP/RAG/venv/bin/python \
  /Users/brunowinter2000/Documents/ai/Meta/ClaudeCode/MCP/RAG/cli.py \
  search_hybrid "attention is all you need" my_collection --top-k 20
```

On error (import failure, DB connection refused): the CLI prints to stderr and exits non-zero. Check PostgreSQL (rag-postgres Docker container) and GPU servers are running via `start.sh`.

# RAG CLI Tools — Reference (Detailed)

## GPU Server Prerequisite

GPU servers (llama-server, SPLADE) are required for search/index operations. The agent starts them automatically via the RAG project `start.sh` if not running.

**RAG_PROJECT_ROOT Resolution (run BEFORE health check):**

The plugin cache contains only code — `data/`, `llama.cpp/`, and `models/` live in the user's RAG project directory. Resolve the path in this order:

```bash
# 1. Read from plugin .env (fastest — set once by user)
RAG_ROOT=$(grep "^RAG_PROJECT_ROOT=" "${CLAUDE_PLUGIN_ROOT}/.env" 2>/dev/null | cut -d'=' -f2)

# 2. Fallback: locate via llama.cpp marker
if [ -z "$RAG_ROOT" ]; then
  RAG_ROOT=$(find ~/Documents -maxdepth 4 -type d -name "llama.cpp" 2>/dev/null | head -1 | xargs -I{} dirname {})
fi

# 3. Still empty → STOP
if [ -z "$RAG_ROOT" ]; then
  echo "RAG_PROJECT_ROOT not found. Add it to ${CLAUDE_PLUGIN_ROOT}/.env"
  exit 1
fi
```

Use `$RAG_ROOT/start.sh` (not `${CLAUDE_PLUGIN_ROOT}/start.sh`) to start GPU servers.
Document fallback path: `$RAG_ROOT/data/documents/<collection>/` when collection not indexed.

The MCP server (list_collections, list_documents, read_document) works without GPU servers.

## Tools

| Tool | Purpose |
|------|---------|
| search_hybrid | Hybrid search (vector + SPLADE + RRF fusion) — best default for large collections |
| search | Semantic search over documents (pure vector) |
| search_keyword | BM25 keyword search for exact terms |
| read_document | Read continuous text from a position |
| list_collections | List all indexed collections |
| list_documents | List documents in a collection |

## Search Workflow

Autonomous workflow — execute phases sequentially without waiting for input.

### Phase 1: EXPLORE

Clarify where to search:
1. `list_collections()` to see available collections
2. `list_documents(collection)` if collection is known but documents are not
3. Identify target collection and narrow scope if possible

### Phase 2: SEARCH

Find initial hits:
1. For large collections (100+ chunks): prefer `search_hybrid` — runs both vector and SPLADE with RRF fusion
2. For small collections or when separate control needed: run `search` AND `search_keyword` in parallel
3. Use 3+ query variations (synonyms, rephrased, different field focus)
4. Assess which hits are relevant

### Phase 3: READ

Deep reading of identified sections:
1. `read_document` with num_chunks=10+ on all relevant hits
2. Extract complete quotes with context
3. Verify context: is the quote relevant to the research question?

### Phase 4: REFINE (if needed)

Targeted follow-up:
1. Additional `search` or `search_keyword` calls based on what was found
2. `read_document` for adjacent sections
3. Continue until research question is answered or exhausted

## Search Techniques

**Direct search:** Research question uses same terminology as documents → search directly.

**HyDE Pattern (Hypothetical Document Embeddings):** When user's question uses different words than the document.
- Problem: "How does X work?" → Document says "The system estimates Y costs..." → no match
- Solution: Generate a hypothetical answer (1-2 sentences), then search with that
- Use when: Conceptual questions, terminology mismatch, direct search returns poor results
- Do NOT use when: Exact terms needed (→ `search_keyword`)

**Keyword search:** Exact terms, parameter names, column names, technical definitions → `search_keyword`.

**Separate searches for distinct terms:** When a query contains multiple distinct entities, run separate searches per entity. Combined queries bias results toward the term with more matches.

## Multi-Citation Strategy

When collection has > 200 chunks OR comprehensive answer needed:

**Strategy A (preferred): Hybrid search handles fusion automatically.**
```
search_hybrid(query="original question", collection="...", top_k=20)
search_hybrid(query="rephrased question with synonyms", collection="...", top_k=20)
```

**Strategy B (when hybrid isn't enough): 3 parallel searches.**
```
search(query="original question", collection="...", top_k=20)
search_keyword(query="specific_term exact_phrase", collection="...", top_k=20)
search(query="rephrased question with synonyms", collection="...", top_k=20)
```

Deduplicate + rank by content fit, not just score.

## Parameter Reference

### search_hybrid

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| query | str | required | Search query (natural language, keywords, or both) |
| collection | str | required | Collection to search in |
| top_k | int | 20 | Number of results (20-50) |
| document | str | None | Filter by document. `%` as wildcard (e.g. `arxiv__%`) |
| neighbors | int | 0 | Include N chunks before/after each match (0-2) |
| rerank | bool | True | Re-score with cross-encoder for higher precision |

**How it works:** Runs 50 vector + 50 BM25 candidates internally, fuses with RRF, optionally reranks with cross-encoder. SPLADE expands synonyms ("revenue" also matches "profit", "earnings").

**When to use:** Default choice for any collection with 100+ chunks. When query mixes concepts and specific terms.

**When NOT to use:** Pure exact-term lookup → `search_keyword`. Very small collections (<50 chunks).

### search

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| query | str | required | Search query (natural language) |
| collection | str | required | Collection to search in |
| top_k | int | 20 | Number of results (20-50) |
| document | str | None | Filter by document. `%` as wildcard |
| neighbors | int | 0 | Include N chunks before/after (0-2) |

**Context Expansion (neighbors):** `neighbors=1` returns [prev] + [match] + [next]. Overlapping matches are deduplicated and merged.

### search_keyword

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| query | str | required | Keywords (space = AND) |
| collection | str | required | Collection to search in |
| top_k | int | 20 | Number of results (20-50) |
| document | str | None | Filter by document. `%` as wildcard |

**Query Syntax:** Multiple words are ANDed. Case insensitive. Stems words ("running" matches "run").

**When to use:** Technical terms, column names, function names, abbreviations, identifiers.

### read_document

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| collection | str | required | Collection name |
| document | str | required | Document name (e.g. "chapter1.md") |
| start_chunk | int | required | Chunk index to start reading from |
| num_chunks | int | 5 | Number of chunks to read (1-20) |

**Drill-Down Pattern:**
```
1. search_hybrid("concept", collection="docs") → finds Chunk: 42
2. read_document(start_chunk=40, num_chunks=10) → read full section
3. search_keyword("exact_term", collection="docs", document="chapter.md") → find exact definition
```

### list_collections

No parameters. Returns all collections with chunk counts.

### list_documents

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| collection | str | required | Collection name |
| document | str | None | Filter by document name. `%` as wildcard |

## Data Structure

```
data/documents/
  {collection}/           <- Filter with collection="..."
    raw/
      {document}.md       <- Original from MinerU
    {document}.md         <- Cleaned version (indexed)
    chunks.json           <- Chunked for indexing
```

## Collection Management

The MCP server has NO delete tool — deletion is a CLI operation.

**Delete a collection (DB + Filesystem):**
```bash
cd <RAG-project-root>
./venv/bin/python workflow.py delete --collection "<name>"
rm -rf data/documents/<name>
```

**Delete a single document within a collection:**
```bash
./venv/bin/python workflow.py delete --collection "<name>" --document "<doc.md>"
```

**Verify:** `list_collections()` after deletion (MCP server restart not needed — reads live from DB).

## Known Limitations

- **GPU servers required** for search/index — MCP server alone only supports list/read operations
- **search results show 500 char abstract preview** — use read_document for full context
- **search_keyword uses stemming** — "running" matches "run" but exact phrase matching is not supported
- **read_document max 20 chunks per call** — for longer sections, make multiple calls with offset
