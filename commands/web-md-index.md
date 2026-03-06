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
 ↓ workflow.py chunk (per file)
directory/*.json (chunks)
 ↓ workflow.py index-json (per file)
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

## Phase 0: Server Lifecycle (Start)

### Step 1: Check Embedding Server

```bash
curl -s localhost:8081/health
```

If `{"status":"ok"}` -> server running, proceed to Step 2.

### Step 2: Start Server (if not running)

```bash
${CLAUDE_PLUGIN_ROOT}/start.sh
```

Wait 5 seconds, verify with health check again.

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

**STOP** - Ask: "Proceed to Phase 2 (Chunk)?"

---

## Phase 2: Chunk

### Data Model

```
collection = parent folder name (e.g. "SearXNG_Docs")
document   = file name (e.g. "index.md", "settings_engines.md")
```

All files in one directory = 1 collection with N documents.

### Step 1: Chunk All Files

For each `.md` file in the directory:

```bash
cd ${CLAUDE_PLUGIN_ROOT} && \
./venv/bin/python workflow.py chunk --input "$MD_DIR/{filename}"
```

This produces a `.json` file next to each `.md` file.

### Step 2: Verify

```bash
ls "$MD_DIR"/*.json | wc -l
```

JSON count should equal MD count.

### PHASE 2 REPORT

```
PHASE 2: Chunk
==============
FILES CHUNKED: [N]
TOTAL CHUNKS:  [N]
OUTPUT:        [directory]/*.json
STATUS:        [Success/Failed]
```

---

**STOP** - Ask: "Proceed to Phase 3 (Index)?"

---

## Phase 3: Index

**Note:** `index-json` deletes only chunks for documents contained in the JSON file, not the entire collection. Safe for adding new documents to existing collections.

### Step 1: Index All JSON Files

For each `.json` file in the directory:

```bash
cd ${CLAUDE_PLUGIN_ROOT} && \
./venv/bin/python workflow.py index-json --input "$MD_DIR/{filename}.json"
```

### Step 2: Verify

```bash
cd ${CLAUDE_PLUGIN_ROOT} && \
./venv/bin/python workflow.py search --query "[topic from crawled site]" --top-k 3
```

### PHASE 3 REPORT

```
PHASE 3: Index
==============
CHUNKS INDEXED: [N]
VERIFIED:       [Yes/No]
```

---

## Phase 4: Server Lifecycle (End)

**STOP** - Ask: "Stop llama-server or keep running for MCP?"

### If Stop:

```bash
pkill -f llama-server
```

### PHASE 4 REPORT

```
PHASE 4: Server Lifecycle
=========================
llama-server: [stopped / kept running for MCP]
```
