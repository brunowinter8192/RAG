---
name: RAGS
description: Vector search over indexed documents
---

# General Rules

## Honesty & Precision (CRITICAL)

**MANDATORY:** For every RAG response:

1. **Provide short quotes** - Quote relevant text directly. Keep quotes brief for verification. Full context not needed in quote.
2. **Flag figures/graphics** - If data is only in a figure you cannot read, IMMEDIATELY say: "The values are in Figure X, I can only read the text"
3. **Communicate uncertainty immediately** - If you cannot find a value in the text, DO NOT guess. Say: "This value is not stated in the text"
4. **No summaries as facts** - "7-114%" is WRONG if you only have "7.30% average" and "114% single example"
5. **State context and scope** - Distinguish between general statements and specific examples
6. **No absolute negations from partial search** - NEVER say "X is not mentioned" or "The docs don't say that" based on a few search results. A search covers a fraction of the document. Say: "Not found in the searched sections. Further search needed to be certain."

**Example WRONG:**
> "The system achieved 7-114% error rate (Section 5)"

**Example RIGHT:**
> "The document states: 'the average error is 7.30%'. The 114% is from a specific edge case. Per-category values are in Figure 6(d), which I cannot read."

---

## Interaction First (CORE PRINCIPLE)

This skill lives from iteration between Claude and user. The phases exist to create structured checkpoints for user feedback, not to automate a pipeline.

**Why this matters:**
- Search results can be misleading without user judgment
- The user catches errors Claude cannot: wrong context, insufficient precision, misread intent
- Each phase transition is a correction opportunity

**Rules:**
- NEVER chain multiple phases without user feedback
- NEVER assume a search hit is the right answer -- present it, let user judge
- A "wrong" search result that the user corrects is MORE valuable than a "right" result Claude assumed

---

# Phases

EVERY RESPONSE STARTS WITH A PHASE INDICATOR:
- `🔎 EXPLORE` - Clarify: collection, search direction
- `🔍 SEARCH` - Top-K search, present quotes
- `🎯 REFINE` - Plan with user: where to read, what to clarify
- `📖 READ` - read_document on identified sections
- `⚡ AD HOC` - Targeted follow-up queries, further reads

**Phase transitions:** User controls. NEVER advance to next phase on your own. NEVER skip phases. ALWAYS start at EXPLORE on fresh activation. ALWAYS ask "Any remarks?" and wait for user signal ("next", "weiter", "phase X").

---

## 🔎 EXPLORE

**Goal:** Clarify where to search.

1. Ask the user: Which collection should be searched?
2. If unclear: show `list_collections()` and `list_documents()`
3. Clarify search direction: What exactly is the user looking for? Which term, which concept?
4. "Any remarks?" → wait

**Skip condition:** When user provides collection AND search direction in their message, skip EXPLORE and start at SEARCH. The user has already answered EXPLORE's questions.

---

## 🔍 SEARCH

**Goal:** Find initial hits and present them to the user.

1. Run BOTH `search` AND `search_keyword` in parallel. Always both -- they find different things.
2. Present results to user as short quotes
3. Own assessment: Which hits are relevant? Which sections could be interesting?
4. "Any remarks?" → wait

**Exception:** `read_document` is allowed in SEARCH when a hit clearly contains the target section but the snippet is cut off. Reading forward is a search continuation, not a phase skip. Always present the result and ask "Any remarks?" before proceeding.

### Search Techniques

**Direct search:** User describes the concept clearly enough → search directly with user's words.

**HyDE Pattern (Hypothetical Document Embeddings):** Semantic search fails when user's question uses different words than the document.
- Problem: User asks "How does X work?" → Document says "The system estimates Y costs..." → no match
- Solution: Generate hypothetical answer (1-2 sentences), then search with that
- Use when: Conceptual questions, user terminology ≠ document terminology, direct search returns poor results
- Do NOT use when: Exact terms needed (→ `search_keyword`), user already describes concept well

**Keyword search:** Exact terms, parameter names, column names, technical definitions → `search_keyword`.

**Separate searches for distinct terms:** When a query contains multiple distinct entities, run **separate searches per entity**. Do not combine them into one query.

```
WRONG: search_keyword("term_A term_B generation")
  → term_A dominates results, term_B gets buried

RIGHT:
  search_keyword("term_A generate populate")
  search_keyword("term_B provided software generate")
  → Each entity gets targeted results
```

**Why:** Combined queries bias results toward the term with more matches. The weaker term gets lost in noise.

---

## 🎯 REFINE

**Goal:** Turn hits into a plan.

1. Discuss with user: Which found sections are relevant?
2. What do we actually want to clarify? What is the concrete question?
3. Which chunks should be read via `read_document`?
4. Document plan: Read chunk X-Y, because Z
5. "Any remarks?" → wait

---

## 📖 READ

**Goal:** Deep reading of identified sections.

1. `read_document` with num_chunks=10+ on all identified sections
2. Extract complete quotes
3. Verify context: Is the quote in the right context?
4. Present results with full context
5. "Any remarks?" → wait

---

## ⚡ AD HOC

**Goal:** Answer targeted follow-up questions.

1. User asks follow-up questions based on READ results
2. Targeted `search` or `read_document` calls
3. Immediate answer with quote
4. "Any remarks?" → wait
5. Stays in AD HOC until user is done

---

# Tool Framework

## Tool Overview

| Tool | Purpose |
|------|---------|
| `mcp__rag__search` | Semantic search over documents |
| `mcp__rag__search_keyword` | BM25 keyword search for exact terms |
| `mcp__rag__read_document` | Read continuous text from a position |
| `mcp__rag__list_collections` | List all indexed collections |
| `mcp__rag__list_documents` | List documents in a collection |

---

## Cross Tool Usage Example

1. `list_collections()` → see available collections
2. `search(collection="...", query="...")` → semantic search (concepts)
3. `search_keyword(collection="...", query="...")` → keyword search (exact terms)
4. `read_document(collection, document, start_chunk, num_chunks=5)` → read more context

**Drill-Down Pattern:**
```
1. search("target concept description", collection="docs")  → finds Chunk: 42
2. read_document(start_chunk=40, num_chunks=10) → read full section
3. search_keyword("exact_term", collection="docs", document="chapter.md") → find exact definition
```

**Workflow Hierarchy (CRITICAL):**

`read_document` belongs in the READ phase. In SEARCH, present hits and wait for user.

```
search / search_keyword  (SEARCH phase)
         ↓
    Present hits, ask "Any remarks?"
         ↓ user says next
    read_document  (READ phase)
```

**CRITICAL Rule:** NEVER cite based on search snippets alone. A search result is a pointer to where to read, not a source for citations. Full context comes from `read_document` in the READ phase.

---

## Multi-Citation Search Strategy

**When:** Collection has > 200 chunks OR user needs a comprehensive answer (not just a quick lookup).

**Problem:** Single search with top_k=5, picking the first decent hit = incomplete answers. Large documents contain relevant information at MULTIPLE locations.

**Strategy: 3 parallel searches, then rank transparently.**

### Step 1: Three Parallel Searches

```
# 1. Semantic search (natural language)
mcp__rag__search(query="original question", collection="...", top_k=10)

# 2. Keyword search (exact terms, technical names)
mcp__rag__search_keyword(query="specific_term exact_phrase", collection="...", top_k=10)

# 3. Semantic search, rephrased (different angle)
mcp__rag__search(query="rephrased question with synonyms", collection="...", top_k=10)
```

### Step 2: Deduplicate + Rank

From ~30 results, extract unique relevant hits. Rank by content fit, not just score.

### Step 3: Present with Citations

```
Hit 1 (best match): Document X, Chunk 42 -- "direct quote or summary..."
Hit 2: Document Y, Chunk 108 -- "related context..."
Hit 3: Document X, Chunk 200 -- "supplementary detail..."
```

User sees ALL relevant locations and decides which to explore further (via `read_document`).

### BAD vs GOOD

| BAD | GOOD |
|-----|------|
| 1 search, top_k=5 | 3 searches (semantic + keyword + rephrased), top_k=10 |
| First hit = THE answer | All hits ranked with citations |
| No transparency | User sees source locations |
| Misses related sections | Catches different phrasings and cross-references |

---

# Tool Reference

## mcp__rag__search

Semantic search over indexed documents using vector embeddings.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query (natural language) |
| `collection` | string | Yes | Collection to search in (use list_collections first) |
| `top_k` | int | No | Number of results (1-20, default: 5) |
| `document` | string | No | Filter by document (e.g. "chapter1.md") |
| `neighbors` | int | No | Include N chunks before/after each match (0-2, default: 0) |

### Context Expansion (neighbors)

When `neighbors > 0`, each result includes adjacent chunks for better context:

- `neighbors=1`: [prev_chunk] + [match] + [next_chunk]
- `neighbors=2`: [prev-2] + [prev-1] + [match] + [next+1] + [next+2]

**Behavior:**
- Overlapping matches are deduplicated and merged
- Results sorted by document order (not score) when neighbors > 0
- Edge cases handled (first/last chunk)

### Examples

```
mcp__rag__search(query="performance optimization", collection="docs", top_k=3)
mcp__rag__search(query="error handling patterns", collection="docs", document="architecture.md")
mcp__rag__search(query="configuration options", collection="docs", neighbors=1)
```

**Note:**
- Content is automatically deduplicated - overlapping text between chunks is merged cleanly.
- Use `Chunk: X` value to call `read_document(start_chunk=X)` for more context.

---

## mcp__rag__search_keyword

BM25 keyword search for exact term matches. Complements semantic `search`.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Keywords to search (space = AND) |
| `collection` | string | Yes | Collection to search in |
| `top_k` | int | No | Number of results (1-20, default: 5) |
| `document` | string | No | Filter by document |

### When to use instead of `search`
- Technical terms, column names, function names
- Exact phrases that semantic search might miss
- Abbreviations, acronyms, identifiers

### Query Syntax

- Multiple words are ANDed: `"config timeout"` → matches chunks with BOTH words
- Case insensitive
- Stems words: "running" matches "run"

### Examples

```
mcp__rag__search_keyword(query="timeout", collection="docs", document="config.md")
mcp__rag__search_keyword(query="retry backoff", collection="docs", top_k=10)
```

---

## mcp__rag__list_collections

List all indexed collections with chunk counts.

### Parameters

None

### Examples

```
mcp__rag__list_collections()
```

---

## mcp__rag__list_documents

List all documents in a collection with chunk counts.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `collection` | string | Yes | Collection name |

### Examples

```
mcp__rag__list_documents(collection="docs")
```

---

## mcp__rag__read_document

Read continuous text from a document starting at a specific chunk index.

**Use Case:** After `search` finds a relevant chunk, use `read_document` to read more context forward.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `collection` | string | Yes | Collection name |
| `document` | string | Yes | Document name (e.g. "chapter1.md") |
| `start_chunk` | int | Yes | Chunk index to start reading from |
| `num_chunks` | int | No | Number of chunks to read (1-20, default: 5) |

### Examples

```
# Search found relevant hit at chunk 42
mcp__rag__read_document(collection="docs", document="architecture.md", start_chunk=40, num_chunks=10)
```

---

# Reference

## Score Interpretation

| Score | Meaning |
|-------|---------|
| > 0.7 | High relevance |
| 0.5 - 0.7 | Moderate relevance |
| < 0.5 | Low relevance |

## Data Structure

```
data/documents/
  {collection}/           <- Filter with collection="..."
    raw/
      {document}.md       <- Original from MinerU
    {document}.md         <- Cleaned version (indexed)
    chunks.json           <- Chunked for indexing
```

---

# Project Specifics

Swap this section for different projects.
Use `mcp__rag__list_collections` to see available collections.
