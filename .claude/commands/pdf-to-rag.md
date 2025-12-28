---
description: Convert PDF to Markdown and index into RAG vector database
argument-hint: [path/to/file.pdf]
allowed-tools: Bash, Read, Write, Edit, Task
---

## Input

PDF Path: $ARGUMENTS

---

## Step Indicator Rule

**MANDATORY:** Every response MUST start with: `Phase X, Step Y: [Name]`

---

## Phase 1: PDF to Markdown

### Step 1: Validate Input

```bash
ls -la "$PDF_PATH"
```

If not found, ask for correct path.

### Step 2: Create Document Folder

Extract filename stem and create folder:

```bash
STEM=$(basename "$PDF_PATH" .pdf)
mkdir -p ./data/documents/$STEM
```

### Step 3: Run MinerU Workflow

```bash
cd ${MINERU_PATH} && \
./venv/bin/python workflow.py convert \
  --input "$PDF_PATH" \
  --output ./data/documents/$STEM/raw.md
```

This runs: MinerU (PDF to MD) + postprocess.py (structural cleanup)

### Step 4: Verify

```bash
ls -la ./data/documents/$STEM/
```

### PHASE 1 REPORT

```
PHASE 1: PDF to Markdown
========================
INPUT: [PDF path]
OUTPUT: data/documents/$STEM/raw.md
STATUS: [Success/Failed]
```

---

**STOP** - Ask: "Proceed to Phase 2 (Chunk + LLM Cleanup)?"

---

## Phase 2: Chunk + LLM Cleanup

### Step 1: Chunk the Document

```python
import sys
sys.path.insert(0, '.')
from src.rag.chunker import chunk_workflow

chunks = chunk_workflow("/path/to/raw.md", strategy="semantic")
print(f"Created {len(chunks)} chunks")
```

### Step 2: LLM Cleanup per Chunk

For EACH chunk, spawn cleanup agent:

```
Task(
  subagent_type="general-purpose",
  model="haiku",
  prompt="Clean this markdown chunk. Fix:
    1. Semantic issues (unclear sentences, broken context)
    2. Residual formatting from PDF extraction
    3. Remove artifacts (page numbers, headers, watermarks)
    4. Fix hyphenation (e.g., 'docu-\\nment' to 'document')

    Do NOT remove incomplete content at chunk boundaries.
    Do NOT add content that isn't there.

    Chunk:
    ---
    [chunk content]
    ---

    Return ONLY cleaned content, no explanation."
)
```

### Step 3: Save as JSON

Write cleaned chunks to `chunks.json`:

```python
import json
from datetime import datetime

output = {
    "source_pdf": "$PDF_PATH",
    "created": datetime.now().isoformat(),
    "chunks": [
        {"index": i, "content": cleaned_chunk}
        for i, cleaned_chunk in enumerate(cleaned_chunks)
    ]
}

with open("data/documents/$STEM/chunks.json", "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
```

### PHASE 2 REPORT

```
PHASE 2: Chunk + LLM Cleanup
============================
CHUNKS: [N]
OUTPUT: data/documents/$STEM/chunks.json
STATUS: [Success/Failed]
```

---

**STOP** - Ask: "Proceed to Phase 3 (Index)?"

---

## Phase 3: Index

### Step 1: Index from JSON

```bash
cd . && \
./venv/bin/python workflow.py index-json \
  --input data/documents/$STEM/chunks.json
```

### Step 2: Verify

```bash
cd . && \
./venv/bin/python workflow.py search --query "[topic from PDF]" --top-k 3
```

### PHASE 3 REPORT

```
PHASE 3: Index
==============
CHUNKS INDEXED: [N]
VERIFIED: [Yes/No]
```

---

## Complete

Document is now searchable via RAG MCP server.

**Files created:**
- `data/documents/$STEM/raw.md` - Human-readable markdown
- `data/documents/$STEM/chunks.json` - Machine-indexed chunks
