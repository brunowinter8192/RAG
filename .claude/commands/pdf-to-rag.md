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

## Phase 1: Convert

### Step 1: Validate Input

Check if PDF exists and is readable:
```bash
ls -la "$PDF_PATH"
```

If file not found, ask user for correct path.

### Step 2: Run MinerU

Execute PDF to Markdown conversion:
```bash
${MINERU_PATH}/venv/bin/mineru \
  -p "$PDF_PATH" \
  -o ./data/raw/
```

### Step 3: Verify Output

Check that MD file was created:
```bash
ls -la ./data/raw/
```

Identify the generated `.md` file.

### PHASE 1 REPORT (MANDATORY)

```
PHASE 1 COMPLETE: Convert
=========================

INPUT: [PDF path]
OUTPUT: [MD path in data/raw/]
STATUS: [Success/Failed]
```

---

**STOP** - Ask user: "Proceed to Phase 2 (Cleanup)?"

**CRITICAL:** Do NOT proceed unless user explicitly confirms.

---

## Phase 2: Cleanup

### Step 1: Launch Cleanup Subagent

Use Task tool to spawn md-cleanup agent:

```
Task(
  subagent_type="general-purpose",
  prompt="Read the markdown file at [path] and fix formatting issues:
    1. Fix broken markdown tables (alignment, missing pipes)
    2. Add missing code block fences, fix language tags
    3. Remove broken image/link references
    4. Normalize heading hierarchy and list formatting

    Return the cleaned content and list of fixes applied."
)
```

### Step 2: Save Cleaned MD

Write cleaned version to `data/documents/`:
```bash
# Copy to documents folder (subagent will have edited in place or provided new content)
cp /path/to/raw/<filename>.md ./data/documents/
```

### PHASE 2 REPORT (MANDATORY)

```
PHASE 2 COMPLETE: Cleanup
=========================

FIXES APPLIED:
- [list of fixes]

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
