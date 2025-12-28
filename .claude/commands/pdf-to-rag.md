---
description: Convert PDF to Markdown and index into RAG vector database
argument-hint: [path/to/file.pdf]
allowed-tools: Bash, Read, Write, Edit, Task
---

## Input

PDF Path: $ARGUMENTS

---

## Step Indicator Rule

**MANDATORY:** Every response in this workflow MUST start with:
`Phase X, Step Y: [Name]`

Example: `Phase 1, Step 2: Run MinerU`

---

## Phase 1: Convert + Pre-Cleanup

### Step 1: Validate Input

Check if PDF exists and is readable:
```bash
ls -la "$PDF_PATH"
```

If file not found, ask user for correct path.

### Step 2: Run MinerU Workflow

Execute PDF to Markdown conversion with automatic pre-cleanup:
```bash
cd ${MINERU_PATH} && \
./venv/bin/python workflow.py convert \
  --input "$PDF_PATH" \
  --output ./data/documents/<filename>.md
```

This runs:
1. MinerU (PDF → Raw MD)
2. postprocess.py (structural cleanup: fences, tables, newlines)
3. Copy to RAG/data/documents/

### Step 3: Verify Output

Check that MD file was created:
```bash
ls -la ./data/documents/
```

### PHASE 1 REPORT (MANDATORY)

```
PHASE 1 COMPLETE: Convert + Pre-Cleanup
=======================================

INPUT: [PDF path]
OUTPUT: [MD path in data/documents/]
PRE-CLEANUP: Applied (fences, tables, newlines)
STATUS: [Success/Failed]
```

---

**STOP** - Ask user: "Proceed to Phase 2 (Chunk + LLM Cleanup)?"

**CRITICAL:** Do NOT proceed unless user explicitly confirms.

---

## Phase 2: Chunk + LLM Cleanup

### Step 1: Chunk the MD File

Use the RAG chunker to split the document:
```python
from src.rag.chunker import chunk_workflow
chunks = chunk_workflow("/path/to/document.md", strategy="semantic")
```

### Step 2: LLM Cleanup per Chunk

For EACH chunk, spawn a cleanup subagent:

```
Task(
  subagent_type="general-purpose",
  model="haiku",
  prompt="Clean this markdown chunk. Fix:
    1. Semantic issues (unclear sentences, broken context)
    2. Formatting that pre-cleanup missed
    3. Remove artifacts from PDF extraction

    Chunk content:
    ---
    [chunk content here]
    ---

    Return ONLY the cleaned content, no explanation."
)
```

### Step 3: Reassemble Document

Collect all cleaned chunks and write back to the MD file.

### PHASE 2 REPORT (MANDATORY)

```
PHASE 2 COMPLETE: Chunk + LLM Cleanup
=====================================

CHUNKS PROCESSED: [N]
FIXES APPLIED: [summary]
OUTPUT: [path in data/documents/]
```

---

**STOP** - Ask user: "Proceed to Phase 3 (Index)?"

**CRITICAL:** Do NOT proceed unless user explicitly confirms.

---

## Phase 3: Index

### Step 1: Index Document

```bash
cd . && \
./venv/bin/python workflow.py index \
  --input-dir ./data/documents \
  --patterns "*.md"
```

### Step 2: Verify

Search for content from the new document to confirm indexing:
```bash
cd . && \
./venv/bin/python workflow.py search --query "[topic from PDF]" --top-k 3
```

### PHASE 3 REPORT (MANDATORY)

```
PHASE 3 COMPLETE: Index
=======================

CHUNKS INDEXED: [N]
VERIFIED: [Yes/No]
READY FOR SEARCH: Yes
```

---

## Complete

Document is now searchable via RAG MCP server.
