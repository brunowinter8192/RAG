# CLAUDE.MD - MCP Server Engineering Reference

## CODE PRINCIPLES

**LEAN** | **SOLID** | **DRY** | **KISS** | **YAGNI**
Long-term thinking. Brutal honesty. No overengineering.

---

## RAG STACK

| Component | Choice | Reason |
|-----------|--------|--------|
| Embedding Model | Qwen3-Embedding-8B (gte-Qwen2-7B) | #1 MTEB, Programming Languages support, 32K context |
| Vector DB | PostgreSQL 18 + pgvector 0.8 | Production-ready, native SQL, HNSW index support |
| MCP Framework | FastMCP | Consistent with other MCP servers |

### Chunking Strategies

| Content Type | Strategy |
|--------------|----------|
| Docs/MD | Semantic chunking (paragraph-aware) |
| Code | Function-level (AST-based where possible) |
| Structured (JSON/YAML) | Keep intact or split by top-level keys |

---

## CRITICAL STANDARDS

- NO comments inside function bodies (only function header comments + section markers)
- NO test files in root (ONLY in debug/ folders - root or per-module)
- NO debug/ or logs/ folders in version control (MUST be in .gitignore)
- NO emojis in production code, READMEs, DOCS.md, logs
- ALWAYS keep script console output concise

**Type hints:** RECOMMENDED but optional

**Fail-Fast:** Let exceptions fly. No try-catch that silently swallows errors affecting business logic. Script must fail if it cannot fulfill its purpose.

---

## server.py PATTERN

**CRITICAL:** server.py is the orchestrator. Only imports and tool definitions.

```python
# INFRASTRUCTURE
from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field

from src.rag.retriever import search_workflow

mcp = FastMCP("RAG")


# TOOLS

@mcp.tool
def search(
    query: Annotated[str, Field(description="Search query to find relevant documents or code")],
    top_k: Annotated[int, Field(description="Number of results (1-20)")] = 5
) -> list[dict]:
    """Use when user needs to find relevant documents, code snippets, or information from indexed knowledge base."""
    return search_workflow(query, top_k)


if __name__ == "__main__":
    mcp.run()
```

**Rules:**
- NO business logic in server.py
- Each tool delegates to module orchestrator
- All parameters use Annotated + Field
- Literal for enum-like choices with clear descriptions

---

## MODULE PATTERN (src/rag/module_name.py)

**CRITICAL:** Each module follows INFRASTRUCTURE -> ORCHESTRATOR -> FUNCTIONS

```python
# INFRASTRUCTURE
import psycopg2
from pgvector.psycopg2 import register_vector

POSTGRES_HOST = "localhost"
POSTGRES_DB = "rag"


# ORCHESTRATOR
def search_workflow(query: str, top_k: int = 5) -> list[dict]:
    conn = get_connection()
    query_vector = embed_query(query)
    results = search_vectors(conn, query_vector, top_k)
    conn.close()
    return format_results(results)


# FUNCTIONS

# Get PostgreSQL connection
def get_connection():
    conn = psycopg2.connect(host=POSTGRES_HOST, dbname=POSTGRES_DB)
    register_vector(conn)
    return conn


# Embed search query
def embed_query(query: str) -> list[float]:
    ...


# Search vectors in PostgreSQL
def search_vectors(conn, query_vector, top_k) -> list:
    ...


# Format results for output
def format_results(results: list) -> list[dict]:
    ...
```

**Section definitions:**

**INFRASTRUCTURE:**
- Imports and constants
- NO functions
- NO logic

**ORCHESTRATOR:**
- ONE function (named: tool_name_workflow)
- Called by server.py tool definition
- Calls internal functions in sequence
- ZERO functional logic (only function composition)

**FUNCTIONS:**
- Ordered by call sequence
- One responsibility each
- Function header comment (one line describing WHAT)
- NO inline comments

---

## TOOL PARAMETER DESIGN

**CRITICAL:** Parameters must be intuitive for LLM understanding

### Two-Layer Documentation (NO DUPLICATION)

**Field Description** = Technical parameter details (what, how, format)
**Docstring** = Semantic use cases (when, why to use this tool)

```python
@mcp.tool
def search(
    query: Annotated[str, Field(description="Search query (e.g., 'authentication patterns', 'error handling')")],
    top_k: Annotated[int, Field(description="Number of results to return (1-20)")] = 5
) -> list[dict]:
    """Use when user needs to find relevant documents, code examples, or information from the indexed knowledge base. Good for answering questions, finding patterns, locating implementations."""
    return search_workflow(query, top_k)
```

**Field tells LLM:** "How do I fill this parameter?"
**Docstring tells LLM:** "When should I call this tool?"

---

## TOOL OUTPUT DESIGN

**CRITICAL:** Output must enable direct tool chaining

### Return Structure
```python
[
    {
        "content": "The actual chunk text...",
        "source": "/path/to/file.md",
        "chunk_index": 0,
        "score": 0.8742
    }
]
```

**Principles:**
- Include all fields needed for context
- Score for ranking/filtering
- Source for attribution
- Human-readable + machine-parseable

---

## ERROR HANDLING

**IMPORTANT:** Fail-fast philosophy

### When to use try-catch
**ALLOWED:**
- Retry logic with exponential backoff
- Graceful degradation with explicit logging
- Resource cleanup (model unloading, connections)

**PROHIBITED:**
- Silently swallowing errors
- Generic `except Exception: pass`
- Hiding failures that affect business logic

FastMCP handles exceptions and communicates errors to client.

---

## DOCUMENTATION STRUCTURE

### Hierarchy

```
RAG/               -> README.md (tree + [See DOCS.md] links)
└── src/rag/       -> DOCS.md (module-level docs)
```

**Principle:** README stops where DOCS begins. No redundancy.

### README Content

README.md contains:
- Quick start / usage
- Directory structure (tree)
- **System configuration** (Docker, ports, breaking changes)
- Troubleshooting / common issues
- Links to DOCS.md for module details

System-level gotchas (version-specific behavior, Docker quirks) belong in README, not DOCS.md.

---

## CLAUDE CODE INTEGRATION (.mcp.json)

**CRITICAL:** Each MCP server needs .mcp.json for Claude Code registration.

### Structure
```json
{
  "mcpServers": {
    "rag": {
      "command": "/absolute/path/to/venv/bin/fastmcp",
      "args": ["run", "/absolute/path/to/server.py"]
    }
  }
}
```

### Rules

**CRITICAL:**
- ALL paths MUST be absolute (no relative paths)
- command: Absolute path to fastmcp executable in venv
- args: ["run", "/absolute/path/to/server.py"]
- NO cwd field (unreliable in Claude Code)

**Verification:**
```bash
claude mcp list
```

---

## NAMING CONVENTIONS

**server.py:** Always named server.py
**Domain folders:** src/rag/ (snake_case)
**Modules:** src/rag/retriever.py, src/rag/indexer.py
**Package markers:** src/__init__.py and src/rag/__init__.py (required for imports)
**Orchestrator function:** tool_name_workflow()
**MCP tool function:** @mcp.tool def tool_name()

---

## COMPLIANCE

Scripts in `debug/` folders (root-level or per-module) are exempt from CLAUDE.md compliance requirements.

All other code must follow these standards strictly.
