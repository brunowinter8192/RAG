---
description: Index a subagent session into RAG for evaluation
argument-hint: [project-path]
---

## Input

Project Path: $ARGUMENTS

---

## Subagent Session Path Format

```
~/.claude/projects/{encoded_project}/*/subagents/agent-*.jsonl
```

Encoding: `/Users/foo/bar` → `Users-foo-bar` (replace `/` with `-`, `_` with `-`)

---

## Phase 1: Find Subagent Sessions

### Step 1: Encode Project Path

```bash
ENCODED=$(echo "$ARGUMENTS" | sed 's|^/||' | sed 's|/|-|g' | sed 's|_|-|g')
echo "Encoded project: $ENCODED"
```

### Step 2: List Subagent Sessions

```bash
find ~/.claude/projects/$ENCODED/*/subagents -name "agent-*.jsonl" 2>/dev/null | head -20
```

### Step 3: Present Options

List found sessions with numbers:
```
[1] agent-abc123.jsonl (2024-01-26 14:30)
[2] agent-def456.jsonl (2024-01-26 15:45)
```

**STOP** - Ask user: "Which subagent to index? (number)"

---

## Phase 2: Convert JSONL to Markdown

### Step 1: Set Variables

```bash
AGENT_ID="<selected agent id from filename>"
JSONL_PATH="<full path to selected jsonl>"
OUTPUT_MD="./data/documents/Subagents/${AGENT_ID}.md"
```

### Step 2: Run Converter

```bash
cd . && \
./venv/bin/python src/rag/jsonl_to_md.py \
    --input "$JSONL_PATH" \
    --output "$OUTPUT_MD"
```

### Step 3: Verify

```bash
head -50 "$OUTPUT_MD"
```

**STOP** - Ask: "Proceed to chunking and indexing?"

---

## Phase 3: Chunk and Index

### Step 1: Chunk the Markdown

```python
import sys
sys.path.insert(0, '.')
from src.rag.chunker import chunk_workflow

chunks = chunk_workflow("$OUTPUT_MD", strategy="fixed", chunk_size=1500, overlap=200)
print(f"Created {len(chunks)} chunks")
```

### Step 2: Save as JSON

```python
import json
from pathlib import Path

output = {
    "document": "$AGENT_ID.md",
    "chunks": [
        {"index": i, "content": c['content']}
        for i, c in enumerate(chunks)
    ]
}

json_path = Path("$OUTPUT_MD").with_suffix('.json')
with open(json_path, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Saved to {json_path}")
```

### Step 3: Index

```bash
cd . && \
./venv/bin/python workflow.py index-json --input data/documents/Subagents/${AGENT_ID}.json
```

---

## Phase 4: Create Tracking Bead

### Step 1: Create Task

Use TaskCreate tool:

```
Subject: [RAG] Indexed subagent: $AGENT_ID
Description:
Subagent session indexed for evaluation.

**Source:** $JSONL_PATH
**Collection:** Subagents
**Document:** $AGENT_ID.md

**Delete after evaluation:**
./venv/bin/python workflow.py delete --collection Subagents --document $AGENT_ID.md
```

---

## Summary Report

```
SUBAGENT INDEXED
================
Agent ID: $AGENT_ID
Source: $JSONL_PATH
Collection: Subagents
Document: $AGENT_ID.md
Tool Calls: [N]
Chunks: [N]

Search: ./venv/bin/python workflow.py search --query "..." --collection Subagents
Delete: ./venv/bin/python workflow.py delete --collection Subagents --document $AGENT_ID.md
```
