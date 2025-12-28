# RAG System for Claude Code

Vector-based retrieval system exposing search via MCP for Claude Code agents.

## Stack

| Component | Choice |
|-----------|--------|
| Embedding | Qwen3-Embedding-8B |
| Vector DB | Qdrant |
| MCP | FastMCP |

## Directory Structure

```
RAG/
├── CLAUDE.md
├── README.md
├── requirements.txt
├── server.py              # MCP Server
├── workflow.py            # CLI for indexing
├── src/
│   └── rag/               [See DOCS.md](src/rag/DOCS.md)
│       ├── embedder.py
│       ├── chunker.py
│       ├── indexer.py
│       └── retriever.py
└── .mcp.json
```

## Usage

### Index Documents

```bash
python workflow.py index --input-dir /path/to/docs
```

### Start MCP Server

```bash
fastmcp run server.py
```

### Claude Code Integration

Register in `.mcp.json`:
```json
{
  "mcpServers": {
    "rag": {
      "command": "/path/to/venv/bin/fastmcp",
      "args": ["run", "/path/to/RAG/server.py"]
    }
  }
}
```

## Roadmap

- [ ] Milestone 1: Foundation (CLAUDE.md, README, requirements)
- [ ] Milestone 2: Embedding Pipeline (embedder, chunker, indexer)
- [ ] Milestone 3: MCP Server (search tool)
- [ ] Milestone 4: Claude Code Agent Integration
