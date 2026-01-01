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
chunks.json
 ↓ embedder + postgres
indexed
```

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

### Step 1: Run md-cleanup-master

```
Task(
  subagent_type="md-cleanup-master",
  prompt="Clean the PDF-converted markdown at ./data/documents/$STEM/raw/$STEM.md. Output to ./data/documents/$STEM/$STEM.md"
)
```

Agent will:
1. Sample file structure
2. Create `debug/clean_$STEM.py`
3. Run script → `$STEM.md` (in parent folder)
4. Report issues fixed

### Step 2: Verify

```bash
grep -c "0_\|1_\|\\\\mathbf" ./data/documents/$STEM/$STEM.md
```

If count > 0: Re-run agent (it will extend its script)
If count = 0: Proceed

### PHASE 2 REPORT

```
PHASE 2: LLM Cleanup
====================
SCRIPT: debug/clean_$STEM.py
OUTPUT: data/documents/$STEM/$STEM.md
REMAINING ISSUES: [N]
STATUS: [Success/Failed]
```

---

**STOP** - Ask: "Proceed to Phase 3 (Chunk)?"

---

## Phase 3: Chunk

### Step 1: Chunk the Document

```python
import sys
sys.path.insert(0, '.')
from src.rag.chunker import chunk_workflow

chunks = chunk_workflow("data/documents/$STEM/$STEM.md", strategy="semantic")
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

with open("data/documents/$STEM/chunks.json", "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
```

### PHASE 3 REPORT

```
PHASE 3: Chunk
==============
CHUNKS: [N]
OUTPUT: data/documents/$STEM/chunks.json
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
  --input data/documents/$STEM/chunks.json
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

## Complete

Document is now searchable via RAG MCP server.

**Files created:**
- `data/documents/$STEM/raw/$STEM.md` - After MinerU + generic postprocess
- `data/documents/$STEM/$STEM.md` - After LLM cleanup
- `data/documents/$STEM/chunks.json` - Chunked for indexing
- `debug/clean_$STEM.py` - Reusable cleanup script
