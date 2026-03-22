# src/ — Source Code Packages

Source code packages for the RAG pipeline.

## Documentation Tree

- [rag/DOCS.md](rag/DOCS.md) — RAG pipeline modules (chunking, embedding, indexing, retrieval)

---

## spawn/tmux_spawn.sh

**Purpose:** Spawn Claude Code worker sessions in isolated tmux sessions with a Ghostty terminal viewer. Provides two functions: `spawn_claude_worker` (prompt from argument) and `spawn_claude_worker_from_file` (prompt from file).
**Input:** Worker name, project path, model name, task prompt or prompt file path. Optional extra Claude CLI flags.
**Output:** tmux pane ID on success. Opens a new Ghostty window attached to the worker's tmux session.
