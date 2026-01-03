---
description: Convert PDF to Markdown and index into RAG vector database
argument-hint: [path/to/file.pdf]
---

## Input

PDF Path: $ARGUMENTS

---

## Pipeline Flow

```
PDF
 ↓ MinerU
 ↓ postprocess.py (generic regex)
raw/{stem}.md
 ↓ md-cleanup-master (creates debug/clean_{stem}.py)
{stem}.md
 ↓ chunker
{stem}.json
 ↓ embedder + postgres
indexed
```

---

## Step Indicator Rule

**MANDATORY:** Every response MUST start with: `Phase X, Step Y: [Name]`

---

## Phase 0: Server Lifecycle (Start)

### Step 1: Check Embedding Server

```bash
curl -s localhost:8081/health
```

If `{"status":"ok"}` → server running, proceed to Phase 1.

### Step 2: Start Server (if not running)

```bash
./start.sh
```

Wait 5 seconds, verify with health check again.

---

## Phase 1: PDF to Markdown

### Step 1: Validate Input

```bash
ls -la "$PDF_PATH"
```

If not found, ask for correct path.

### Step 2: Create Document Folder

```bash
STEM=$(basename "$PDF_PATH" .pdf)
mkdir -p ./data/documents/$STEM/raw
```

### Step 3: Run MinerU Workflow

```bash
cd ${MINERU_PATH} && \
./venv/bin/python workflow.py convert \
  --input "$PDF_PATH" \
  --output ./data/documents/$STEM/raw/$STEM.md
```

Output: `raw/{stem}.md` = MinerU output + generic postprocess.py cleanup

### Step 4: Verify

```bash
ls -la ./data/documents/$STEM/
```

### PHASE 1 REPORT

```
PHASE 1: PDF to Markdown
========================
INPUT: [PDF path]
OUTPUT: data/documents/$STEM/raw/$STEM.md
STATUS: [Success/Failed]
```

---

**STOP** - Ask: "Proceed to Phase 2 (LLM Cleanup)?"

---

## Phase 2: LLM Cleanup

Agent analyzes raw/{stem}.md, creates cleanup script, outputs {stem}.md in parent folder.

### Step 0: Activate agent-dispatch Skill (if not active)

**BEFORE running the subagent, you MUST activate the agent-dispatch skill:**
```
Skill('agent-dispatch')
```
Skip this step if agent-dispatch is already active in this session.

### Step 1: Run md-cleanup-master

Use the Task tool with subagent_type='md-cleanup-master'.

Agent will:
1. Sample file structure
2. Create `debug/clean_$STEM.py`
3. Run script → `$STEM.md` (in parent folder)
4. Report issues fixed

**STOP** - Ask: "Proceed to Phase 3 (Chunk)?"

---

## Phase 3: Chunk

### Step 1: Chunk the Document

```python
import sys
sys.path.insert(0, '.')
from src.rag.chunker import chunk_workflow

chunks = chunk_workflow("data/documents/$STEM/$STEM.md")
print(f"Created {len(chunks)} chunks")
```

### Step 2: Save as JSON

```python
import json
from datetime import datetime

output = {
    "source_pdf": "$PDF_PATH",
    "created": datetime.now().isoformat(),
    "chunks": [
        {"index": i, "content": c['content'], "source": c['source']}
        for i, c in enumerate(chunks)
    ]
}

with open("data/documents/$STEM/$STEM.json", "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
```

### PHASE 3 REPORT

```
PHASE 3: Chunk
==============
CHUNKS: [N]
OUTPUT: data/documents/$STEM/$STEM.json
STATUS: [Success/Failed]
```

---

**STOP** - Ask: "Proceed to Phase 4 (Index)?"

---

## Phase 4: Index

### Step 1: Index from JSON

```bash
cd . && \
./venv/bin/python workflow.py index-json \
  --input data/documents/$STEM/$STEM.json
```

### Step 2: Verify

```bash
cd . && \
./venv/bin/python workflow.py search --query "[topic from PDF]" --top-k 3
```

### PHASE 4 REPORT

```
PHASE 4: Index
==============
CHUNKS INDEXED: [N]
VERIFIED: [Yes/No]
```

---

## Phase 5: Server Lifecycle (End)

**STOP** - Ask: "Stop llama-server or keep running for MCP?"

### If Stop:

```bash
pkill -f llama-server
```

### PHASE 5 REPORT

```
PHASE 5: Server Lifecycle
=========================
llama-server: [stopped / kept running for MCP]
```