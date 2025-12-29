---
description: Debug RAG system issues (llama.cpp, PostgreSQL, embedding pipeline)
argument-hint: [error-description or symptom]
---

## Problem Observation

User observes: $ARGUMENTS

---

## Step Indicator Rule

**MANDATORY:** Every response MUST start with: `Phase X, Step Y: [Name]`

---

## Phase 1: Service Status Check

### Step 1: Check Running Services

```bash
# PostgreSQL
docker ps --filter name=rag-postgres --format "{{.Names}}: {{.Status}}"

# llama.cpp embedding server
lsof -i :8081 | head -2

# Check indexed documents
docker exec rag-postgres psql -U rag -d rag -c "SELECT source, COUNT(*) FROM documents GROUP BY source;"
```

### Step 2: Check Server Logs (if llama.cpp running in background)

**CRITICAL:** Server logs often reveal the exact crash point.

Look for:
- Token counts per request
- `n_ubatch` vs `n_tokens` mismatches
- Memory allocation errors
- GGML assertions

### Step 3: Test Embedding Endpoint

```bash
curl -s http://localhost:8081/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": ["test"], "model": "Qwen3-Embedding-8B"}' | head -c 200
```

### PHASE 1 REPORT

```
PHASE 1: Service Status
=======================
PostgreSQL: [UP/DOWN]
llama.cpp:  [UP/DOWN on :8081]
Documents:  [N chunks indexed]
Embedding:  [Working/Failed]
```

---

**STOP** - Ask: "Services OK? Proceed to Phase 2 (Code Investigation)?"

---

## Phase 2: Code Investigation

### Step 1: Read DOCS.md

**MANDATORY:** Read `src/rag/DOCS.md` before any code exploration.

### Step 2: Trace the Pipeline

```
workflow.py → indexer.py → embedder.py → httpx → llama.cpp:8081
                ↓
            PostgreSQL (pgvector)
```

### Step 3: Check Historical Bugs

Read `bug_fixes/` for similar issues and previous fixes.

### Step 4: Identify Crash Point

Use logs + code tracing to pinpoint exact failure location.

### PHASE 2 REPORT

```
PHASE 2: Code Investigation
===========================
DOCS.md:    [Read/Skipped]
Crash Point: [file:line]
Historical:  [Related bug_fixes or None]
```

---

**STOP** - Ask: "Proceed to Phase 3 (Root Cause Analysis)?"

---

## Phase 3: Root Cause Analysis

### Step 1: Web Search (if needed)

Search pattern: `llama.cpp [error message] [year]`

### Step 2: Formulate Hypothesis

```
ROOT CAUSE
==========
Component: [llama.cpp / embedder.py / indexer.py / PostgreSQL]
Issue:     [What's wrong]
Evidence:  [Log lines, error messages]
```

### Step 3: Propose Fix

```
PROPOSED FIX
============
[Concrete fix with file:line references]
```

---

**STOP** - Ask: "Proceed to implementation?"

---

## Phase 4: Implementation + Documentation

1. Implement fix
2. Test with: `./venv/bin/python workflow.py search --query "test" --top-k 1`
3. Document in `bug_fixes/YYYY-MM-DD_[name].md`

---

## Common Issues Quick Reference

| Symptom | Likely Cause | Quick Check |
|---------|--------------|-------------|
| Server disconnected | ubatch < tokens | Check server log for token counts |
| Connection refused | llama.cpp not running | `lsof -i :8081` |
| Empty results | No indexed docs | Check PostgreSQL count |
| Slow embedding | Large batch size | Check BATCH_SIZE in indexer.py |
