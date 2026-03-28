---
description: Index website-crawled Markdown files into RAG (cleanup + chunk + embed)
argument-hint: [path/to/md-directory]
---

## Input

MD Directory: $ARGUMENTS

---

## Pipeline Flow

```
directory/*.md (raw crawl4ai output)
 ↓ web-md-cleanup agent (remove nav, footer, UI chrome)
directory/*.md (cleaned)
 ↓ workflow.py index-dir (ensures servers, chunks, indexes — one call)
indexed in RAG
```

---

## Step Indicator Rule

**MANDATORY:** Every response MUST start with: `Phase X, Step Y: [Name]`

---

## STOP Point Rule

**CRITICAL:** After each phase, there is a `**STOP**` marker.

- **STOP = END OF RESPONSE.** Do not continue to next phase.
- Wait for user to say "weiter", "proceed", "phase X", etc.
- "weiter" = proceed to NEXT phase only, not "run all remaining phases"
- NEVER batch multiple phases in one response

---

## Phase 1: Web MD Cleanup

### Step 1: Validate Input

```bash
ls "$MD_DIR"/*.md | wc -l
```

If no MD files found, ask for correct path.

### Step 2: Run web-md-cleanup agent

Use the Task tool with subagent_type='web-md-cleanup'.

Prompt the agent with:
```
Clean up the website-crawled markdown files in this directory.

INPUT DIRECTORY: $MD_DIR
All .md files in this directory are raw crawl4ai output with website chrome.

Sample 3-5 files first to identify common navigation/footer patterns,
then build a single cleanup script that processes all files.
```

Agent will:
1. Sample files to identify patterns
2. Create `debug/clean_web_{dirname}.py`
3. Run script on all files
4. Report patterns found and char reduction

### Step 3: Verify Cleanup (you, not the agent)

**CRITICAL:** Never trust subagent output. Verify independently.

1. **Spot-check:** Read first 20 lines of 2-3 cleaned files. Should start with content, not navigation.
2. **Source comments preserved:** `grep -l "<!-- source:" "$MD_DIR"/*.md | wc -l` should equal total file count.
3. **Char reduction:** Compare total chars before/after. 10-50% reduction is expected. More than 60% = possible content loss.

If cleanup failed -> STOP and inform user.

### PHASE 1 REPORT

```
PHASE 1: Web MD Cleanup
========================
INPUT:    [directory]
FILES:    [N] markdown files
PATTERNS: [list of detected patterns]
REDUCTION: [X%] char reduction
STATUS:   [Success/Failed]
```

---

**STOP** - Ask: "Proceed to Phase 2 (Index)?"

---

## Phase 2: Chunk + Index

### Step 1: Run index-dir

**Single command** — ensures servers are running, chunks all .md files, indexes all chunks:

```bash
cd ~/Documents/ai/Meta/ClaudeCode/MCP/RAG && \
./venv/bin/python workflow.py index-dir --input "$MD_DIR"
```

This handles everything: server health check → start if needed → chunk → index → summary.

### Step 2: Verify

```bash
cd ~/Documents/ai/Meta/ClaudeCode/MCP/RAG && \
./venv/bin/python workflow.py search --query "[topic from crawled site]" --top-k 3
```

### PHASE 2 REPORT

```
PHASE 2: Chunk + Index
=======================
CHUNKS INDEXED: [N]
VERIFIED:       [Yes/No]
```

---

## Phase 3: Server Lifecycle (End)

**STOP** - Ask: "Stop GPU servers or keep running for MCP?"

### If Stop:

```bash
cd ~/Documents/ai/Meta/ClaudeCode/MCP/RAG && \
./venv/bin/python workflow.py server stop
```

### PHASE 3 REPORT

```
PHASE 3: Server Lifecycle
=========================
GPU servers: [stopped / kept running for MCP]
```
