---
name: RAG_MCP
description: Vector search over indexed documents
---

# RAG MCP Tool Usage

## Tool: `mcp__rag__search`

Semantic search over indexed documents using vector embeddings.

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query (natural language) |
| `top_k` | int | No | Number of results (1-20, default: 5) |
| `collection` | string | No | Filter by collection (folder name in data/documents/) |
| `document` | string | No | Filter by document (e.g. "chapter1.md") |

---

## When to Use

Use RAG search when:
- User asks about content in indexed documents
- User needs specific information from the knowledge base
- Answering questions that require document context

Do NOT use when:
- Information is in codebase files (use Grep/Read instead)
- User asks about general knowledge (use your training data)
- Document hasn't been indexed yet

---

## Examples

### Basic Search
```
mcp__rag__search(query="TPC-H benchmark performance", top_k=3)
```

### Filter by Collection
```
mcp__rag__search(query="pricing requirements", collection="specification")
```

### Filter by Document
```
mcp__rag__search(query="query execution", collection="specification", document="specification.md")
```

---

## Output Format

```
--- Result 1 (score: 0.7421) ---
Collection: specification | Document: specification.md
[content snippet, max 500 chars]

--- Result 2 (score: 0.6812) ---
Collection: specification | Document: specification.md
[content snippet, max 500 chars]
```

---

## Score Interpretation

| Score | Meaning |
|-------|---------|
| > 0.7 | High relevance |
| 0.5 - 0.7 | Moderate relevance |
| < 0.5 | Low relevance |

---

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

## Indexed Collections

Check available collections:
```bash
ls data/documents/
```

Current: `specification` (TPC-H specification)
