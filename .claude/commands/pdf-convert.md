---
description: Convert PDF to Markdown and index into RAG vector database
argument-hint: [path/to/file.pdf]
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

## Phase 2: Chunk + Cleanup

**Strategy:** Script-first, Agent only for semantic issues scripts can't fix.

### Step 1: Chunk the Document

```python
import sys
sys.path.insert(0, '.')
from src.rag.chunker import chunk_workflow

chunks = chunk_workflow("data/documents/$STEM/raw.md", strategy="semantic")
print(f"Created {len(chunks)} chunks")
```

### Step 2: Scan for Semantic Issues

Analyze chunks for issues that scripts CANNOT fix:

```python
import re

issues = []
for c in chunks:
    content = c['content']
    chunk_issues = []

    # OCR errors (numbers in words)
    if re.search(r'\b\w*[0-9]\w+[a-z]\w*\b', content):
        chunk_issues.append('ocr')

    # Run-on sentences (lowercase followed by uppercase mid-word)
    if re.search(r'[a-z][A-Z][a-z]', content):
        chunk_issues.append('run-on')

    if chunk_issues:
        issues.append({'index': c['chunk_index'], 'types': chunk_issues})

print(f"Found {len(issues)} chunks with semantic issues")
```

### Step 3: Agent Cleanup (only if needed)

**Only for chunks with semantic issues:**

```
Task(
  subagent_type="md-cleanup-master",
  prompt="[chunk content with issues]"
)
```

**If no semantic issues:** Skip agent, use chunks as-is.

### Step 4: Save as JSON

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

with open("data/documents/$STEM/chunks.json", "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
```

### PHASE 2 REPORT

```
PHASE 2: Chunk + Cleanup
========================
CHUNKS: [N]
SEMANTIC ISSUES: [M] chunks required agent cleanup
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
