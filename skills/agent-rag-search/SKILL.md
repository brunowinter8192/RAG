---
name: agent-rag-search
---

# RAG CLI Tools — Reference

## CLI Invocation

All tools are invoked via the `rag-cli` wrapper (installed at `~/.local/bin/rag-cli`, in PATH):

```bash
rag-cli <cmd> [args]
```

### Quick Reference — All 6 Tools

```bash
# Discovery
rag-cli list_collections
rag-cli list_documents my_collection
rag-cli list_documents my_collection --document "arxiv_%"

# Search
rag-cli search_hybrid "transformer attention mechanism" my_collection --top-k 20
rag-cli search_hybrid "cost function" my_collection --document "paper.md"
rag-cli search_hybrid "query" my_collection --no-rerank   # faster, lower precision

rag-cli search "semantic similarity" my_collection --top-k 30
rag-cli search_keyword "learning_rate dropout" my_collection --top-k 20

# Read
rag-cli read_document my_collection paper.md 42
rag-cli read_document my_collection paper.md 42 --before 2 --after 5
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

Read-only commands (`list_collections`, `list_documents`, `read_document`) don't need GPU servers — DB reads only. Search commands (`search`, `search_hybrid`, `search_keyword`) need the embedding server running.

## GPU Server Interaction

- **Status:** `rag-cli server status` — table: name, port, status, PID, healthy.
- **Control:** `rag-cli server start|stop|restart [name]` — without `name`, all three.
- **Debug:** `rag-cli server tail [name] [-n 30]` for llama-server output, `rag-cli server errors [--today] [--verbose]` for structured errors.

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
1. `rag-cli list_collections` to see available collections
2. `rag-cli list_documents <collection>` if collection is known but documents are not
3. Identify target collection and narrow scope if possible

### Phase 2: SEARCH

Find initial hits:
1. For large collections (100+ chunks): prefer `rag-cli search_hybrid` — runs both vector and SPLADE with RRF fusion
2. For small collections or when separate control needed: run `rag-cli search` AND `rag-cli search_keyword` in parallel
3. Use 3+ query variations (synonyms, rephrased, different field focus)
4. Assess which hits are relevant

### Phase 3: READ

Deep reading of identified sections:
1. `rag-cli read_document <collection> <document> <chunk_index> --before 2 --after 5` on all relevant hits
2. Extract complete quotes with context
3. Verify context: is the quote relevant to the research question?

### Phase 4: REFINE (if needed)

Targeted follow-up:
1. Additional `rag-cli search` or `rag-cli search_keyword` calls based on what was found
2. `rag-cli read_document` for adjacent sections
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
```bash
rag-cli search_hybrid "original question" <collection> --top-k 20
rag-cli search_hybrid "rephrased question with synonyms" <collection> --top-k 20
```

**Strategy B (when hybrid isn't enough): 3 parallel searches.**
```bash
rag-cli search "original question" <collection> --top-k 20
rag-cli search_keyword "specific_term exact_phrase" <collection> --top-k 20
rag-cli search "rephrased question with synonyms" <collection> --top-k 20
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

**Context expansion:** use `read_document` with `--before`/`--after` on promising hits to read surrounding chunks.

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
| chunk_index | int | required | Anchor chunk index (from search hit) |
| before | int | 0 | Chunks to read before the anchor (0–10) |
| after | int | 0 | Chunks to read after the anchor (0–10) |

**Context expansion:** `read_document(chunk_index=42, before=2, after=5)` returns chunks 40–47. Overlapping chunks are deduplicated and merged.

**Drill-Down Pattern:**
```bash
rag-cli search_hybrid "concept" docs                           # → finds Chunk: 42 in chapter.md
rag-cli read_document docs chapter.md 42 --before 2 --after 5  # → read surrounding section
rag-cli search_keyword "exact_term" docs --document chapter.md # → find exact definition
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
rag-cli delete --collection "<name>"
rm -rf <RAG-project-root>/data/documents/<name>
```

**Delete a single document within a collection:**
```bash
rag-cli delete --collection "<name>" --document "<doc.md>"
```

**Verify:** `rag-cli list_collections` after deletion (reads live from DB).

## Known Limitations

- **GPU servers required** for search/index — MCP server alone only supports list/read operations
- **search results show 500 char abstract preview** — use read_document for full context
- **search_keyword uses stemming** — "running" matches "run" but exact phrase matching is not supported
- **read_document max 10 chunks before + 10 after per call** — for longer sections, make multiple calls with shifted chunk_index

## Autonomous Operation

You CANNOT ask questions — not to the user, not to the caller.
NEVER return questions, clarification requests, or "before I proceed" prompts.
When information is missing or ambiguous, make your best judgment, proceed with research, and document assumptions in your output.
ALWAYS return concrete findings (quotes, chunk references, document paths). If uncertain, flag it but STILL return what you found.

**No filler prose:** Every sentence in your response must carry information the caller can act on. Do not open with "Perfect!", "I now have comprehensive information", "Let me compile", or any phrase that conveys nothing. Start directly with findings.

## Output Format

**Every finding MUST include document path + chunk reference + direct quote.**

```
## Findings

### 1. <Topic/Answer>
**Collection:** <collection>
**Document:** <document.md>
**Chunk:** <chunk number>
**Quote:** "<direct quote from the text>"
**Context:** <1-2 sentences explaining relevance>

### 2. <Topic/Answer>
...

## Not Found
- <what was searched for but not found>
- <which queries were tried>

## Search Metadata
**Queries Used:** query1, query2, query3, ...
**Collections Searched:** collection1, collection2
**Total Hits Reviewed:** N
**Documents Read (read_document):** N
```

## Honesty Rules (RAG-Specific)

- **Provide short quotes** — quote relevant text directly for verification
- **Flag figures/graphics** — if data is only in a figure: "The values are in Figure X, I can only read the text"
- **No absolute negations from partial search** — NEVER say "X is not mentioned". Say: "Not found in the searched sections. Further search needed to be certain."
- **No summaries as facts** — "7-114%" is WRONG if you only have "7.30% average" and "114% single example"

## Persisted-Output Handling

`rag-cli search*` results regularly exceed CC's inline tool-output limit and get persisted (`<persisted-output>` block, file path under `tool-results/<id>.txt`). Typical size: 30-50 KB for `--top-k 15-20` with rerank enabled.

**Rule: read the persisted file FULLY in ONE Read call.** No offset/limit chunking, no incremental "first 100 lines, then more". A 50 KB persisted file is ~400-500 lines in `cat -n` format and fits well below Read's 2000-line default — one call covers it.

```
WRONG: Read(file_path=..., offset=0, limit=100) → Read(offset=100, limit=200) → ...
RIGHT: Read(file_path=...)   # whole file, one call
```

If the persisted file is so large it won't fit (>200 KB / >2000 lines): the search itself was too broad. Re-issue with smaller `--top-k` or tighter query — don't paginate the read.

## When to Stop

- Found the specific answer with quotes → STOP immediately
- Research task: minimum 3 query variations, stop when 5+ relevant hits found
- After search: switch to `read_document` for full context on best hits
- If GPU servers are not running → STOP and report the startup command to the user
- If `rag-cli list_collections` returns "No collections indexed." → STOP immediately. Return: "No collections indexed. Re-index the target collection first via `workflow.py index-dir` (run from RAG project root — indexing is not yet exposed via rag-cli)." Do NOT fall back to Bash file reads.
