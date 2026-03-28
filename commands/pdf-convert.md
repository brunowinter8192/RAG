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
{stem}.md  ← raw state, directly in collection folder
 ↓ md-cleanup-master (works in /tmp only, overwrites {stem}.md)
{stem}.md  ← clean state
 ↓ chunker
{stem}.json
 ↓ embedder + postgres
indexed
```

**Collection states (EXACTLY TWO):**
- **Raw:** `{stem}.md` = MinerU output, no cleanup done yet
- **Clean:** `{stem}.md` = fully cleaned, ready for indexing

No `raw/` subfolder. No `debug/` subfolder. All process artifacts go to `/tmp/`.

---

## Step Indicator Rule

**MANDATORY:** Every response MUST start with: `Phase X, Step Y: [Name]`

---

## STOP Point Rule

**CRITICAL:** After each phase report, there is a `**STOP**` marker.

- **STOP = END OF RESPONSE.** Do not continue to next phase.
- Wait for user to say "weiter", "proceed", "phase X", etc.
- "weiter" = proceed to NEXT phase only, not "run all remaining phases"
- NEVER batch multiple phases in one response

---

## Phase 1: PDF to Markdown

### Step 1: Validate Input

```bash
ls -la "$PDF_PATH"
```

If not found, ask for correct path.

### Step 2: Create Document Folder

**Naming Convention (MANDATORY):**
- Collection name MUST be descriptive: `Qwen3_Embedding_Paper`, `SPLADE_Architecture`, `RAG_Survey_2024`
- NEVER use ArXiv IDs (`2506.05176`) or cryptic identifiers as collection names
- Ask user for a descriptive name if the PDF filename is not self-explanatory
- Format: PascalCase_With_Underscores, no spaces

```bash
STEM="<descriptive_name>"  # NOT $(basename "$PDF_PATH" .pdf) if filename is cryptic
mkdir -p ${CLAUDE_PLUGIN_ROOT}/data/documents/$STEM
```

### Step 3: Run MinerU Workflow

```bash
cd ${MINERU_PATH} && \
./venv/bin/python workflow.py convert \
  --input "$PDF_PATH" \
  --output ${CLAUDE_PLUGIN_ROOT}/data/documents/$STEM/$STEM.md
```

Output: `{stem}.md` = MinerU output + generic postprocess.py cleanup (raw state, directly in collection folder)

### Step 4: Verify

```bash
ls -la ${CLAUDE_PLUGIN_ROOT}/data/documents/$STEM/
```

### PHASE 1 REPORT

```
PHASE 1: PDF to Markdown
========================
INPUT: [PDF path]
OUTPUT: data/documents/$STEM/$STEM.md  (raw state)
STATUS: [Success/Failed]
```

---

**STOP** - Ask: "Proceed to Phase 2 (LLM Cleanup)?"

---

## Phase 2: LLM Cleanup

Agent reads `{stem}.md` (raw state), fixes artifacts via scripts in `/tmp/`, overwrites `{stem}.md` with the clean version.

### Step 1: Run md-cleanup-master

Use the Agent tool with subagent_type='rag:md-cleanup-master'.

Agent will:
1. Sample file structure
2. Create cleanup scripts in `/tmp/fix_{issue}_{stem}.py` (NEVER in collection folder)
3. Overwrite `{stem}.md` with clean version (same path — raw → clean in place)
4. Report issues fixed

### Step 2: Verify Cleanup (you, not the agent)

**CRITICAL:** Never trust subagent output. Verify independently.

1. **Grep for claimed fixes** - For each pattern the agent claims to have fixed, grep BOTH raw and clean file:
   - Raw file must show matches (confirms pattern existed)
   - Clean file must show 0 matches (confirms fix applied)
2. **Stichprobe Content** - Read 10-15 lines from the middle of both files side-by-side, confirm no content loss beyond the fixes
3. **Line count** - Compare `wc -l` of raw vs clean. Should be stable (equal or very close)

Report verification result in table format:

```
| Pattern | Raw | Clean | Status |
|---------|-----|-------|--------|
| [pattern] | N matches | 0 matches | OK/FAIL |
```

If any FAIL → STOP and inform user.

**STOP** - Ask: "Proceed to Phase 3 (Chunk)?"

---

## Phase 3: Chunk + Index

### Data Model

```
collection = folder name (e.g. "Thesis")
document   = file name (e.g. "1.Einleitung.md", "2.Grundlagen.md")
```

**Multiple MD files in one folder:**
- 1 collection with N documents
- Filterable in search: `search(collection="Thesis", document="A_Setup.md")`

**Incremental Indexing:** When adding a new document to an existing collection, `index-dir` handles it — existing chunks for that document are replaced, other documents in the collection are untouched.

### Step 1: Run index-dir

**Single command** — ensures servers are running, chunks all .md files, indexes all chunks:

```bash
cd ~/Documents/ai/Meta/ClaudeCode/MCP/RAG && \
./venv/bin/python workflow.py index-dir --input data/documents/$STEM/
```

If the document lives in a subdirectory of an existing collection, use `--collection` to override:

```bash
./venv/bin/python workflow.py index-dir --input data/documents/linkedin/papers/ --collection linkedin
```

### Step 2: Verify

```bash
cd ~/Documents/ai/Meta/ClaudeCode/MCP/RAG && \
./venv/bin/python workflow.py search --query "[topic from PDF]" --top-k 3
```

### PHASE 3 REPORT

```
PHASE 3: Chunk + Index
=======================
CHUNKS INDEXED: [N]
VERIFIED: [Yes/No]
```

---

## Phase 4: Server Lifecycle (End)

**STOP** - Ask: "Stop GPU servers or keep running for MCP?"

### If Stop:

```bash
cd ~/Documents/ai/Meta/ClaudeCode/MCP/RAG && \
./venv/bin/python workflow.py server stop
```

### PHASE 4 REPORT

```
PHASE 4: Server Lifecycle
=========================
GPU servers: [stopped / kept running for MCP]
```