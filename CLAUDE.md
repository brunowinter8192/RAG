# CLAUDE.MD - MCP Server Engineering Reference

## PROJECT

- **GitHub Repo:** `brunowinter8192/RAG`
- **Bugs:** GitHub Issues (`gh issue create --repo brunowinter8192/RAG`)

---

## CONFIGURATION

Editable files for Process Improvements in RECAP/IMPROVE phase:

| Config | Path | Purpose |
|--------|------|---------|
| Project Standards | `CLAUDE.md` | Code conventions, MCP patterns, naming |
| Iterative Dev | `.claude/skills/iterative-dev/SKILL.md` | PLAN-IMPLEMENT-RECAP-IMPROVE-CLOSING cycle |
| MCP Usage | `.claude/skills/mcp_usage/SKILL.md` | MCP tool docs, parameters, usage strategy |
| Explore Agent | `.claude/skills/agent-explore/SKILL.md` | Explore agent dispatch rules |
| Explore Instructions | `.claude/agents/explore-specialist.md` | Codebase search subagent instructions |
| MD Cleanup Instructions | `.claude/agents/md-cleanup.md` | Markdown cleanup subagent instructions |
| PDF Convert Command | `.claude/commands/pdf-convert.md` | PDF-to-RAG pipeline command |
| Debug Command | `.claude/commands/debug.md` | Debug RAG system issues |


---

## CRITICAL STANDARDS

- NO comments inside function bodies (only function header comments + section markers)
- NO test files in root (ONLY in debug/ folders - root or per-module)
- NO debug/ or logs/ folders in version control (MUST be in .gitignore)

**Type hints:** RECOMMENDED but optional

**Fail-Fast:** Let exceptions fly. No try-catch that silently swallows errors affecting business logic. Script must fail if it cannot fulfill its purpose.

---

## General

- NO emojis in production code, READMEs, DOCS.md, logs
- ALWAYS keep script console output concise

For system configuration, hardware specs, and parameter details: **See README.md**

### Plugin Distribution

Plugin (`/plugin install rag@brunowinter-plugins`) ships only 3 components:

| Component | Source (edit here) | Plugin target (auto-generated) |
|-----------|--------------------|-------------------------------|
| Skill | `.claude/skills/mcp_usage/*` | `skills/mcp_usage/*` |
| MCP Config | inline in `.claude-plugin/plugin.json` | `mcpServers` field |
| Command | `.claude/commands/pdf-convert.md` | `commands/pdf-convert.md` |

**NOT in plugin:** debug, index-subagent, explore-agent, md-cleanup -- these are local dev tools only.

**pre-commit hook** (`.git/hooks/pre-commit`) syncs Skill + Command automatically.

**Path substitution** (commands only):
- Absolute repo root -> `${CLAUDE_PLUGIN_ROOT}`
- `/Users/*/Documents/ai/Mineru` -> `${MINERU_PATH}`

**Rules:**
- ALWAYS edit `.claude/` files, NEVER `.claude-plugin/` directly
- `.claude-plugin/` is the distribution folder -- auto-generated
- Hook runs on every `git commit` -- no manual sync needed

### Testing

**CRITICAL:** Test MCP tools by calling them directly via MCP tool calls, NOT via Python import.

**RIGHT:**
```
mcp__rag__search(query="test query", top_k=5)
```

**WRONG:**
```bash
source venv/bin/activate && python -c "from src.rag.retriever import ..."
```

**Rules:**
- The MCP server runs as a separate process - there is no local venv to activate
- Always use `mcp__rag__<tool_name>(...)` to verify tool behavior
- **After code changes:** MCP server must be restarted before tool calls reflect changes. Ask user to restart (`/mcp` in Claude Code) before running verification tests

---

## server.py (MCP Entry Point)

**Purpose:** MCP server exposing tools to Claude Code. Only imports and tool definitions.

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

## workflow.py (Pipeline Entry Point)

**Purpose:** CLI for pipeline operations (chunking, indexing). Human-triggered, not MCP.

```python
# INFRASTRUCTURE
import argparse

# From src/rag/indexer.py: Index chunks into PostgreSQL
from src.rag.indexer import index_json_workflow

# From src/rag/retriever.py: Search indexed documents
from src.rag.retriever import search_workflow


# ORCHESTRATOR
def main(command: str, **kwargs) -> None:
    if command == "index-json":
        count = index_json_workflow(kwargs["input"])
        print(f"Indexed {count} chunks from JSON")

    elif command == "search":
        results = search_workflow(kwargs["query"], kwargs.get("top_k", 5))
        for r in results:
            print(f"[{r['score']:.2f}] {r['source']}: {r['content'][:100]}...")


if __name__ == "__main__":
    # argparse setup...
    main(args.command, **kwargs)
```

**Rules:**
- Filename MUST be `workflow.py` at project root
- Imports from src/ package using absolute imports
- Only INFRASTRUCTURE + ORCHESTRATOR sections
- No FUNCTIONS section (delegates to modules)

**Usage:**
```bash
./venv/bin/python workflow.py index-json --input ./data/documents/paper1/chunks.json
./venv/bin/python workflow.py search --query "your query" --top-k 5
```

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
