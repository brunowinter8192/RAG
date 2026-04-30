---
name: pdf-convert
description: Convert PDF to Markdown via MinerU, LLM-cleanup, chunk and index into RAG collection. Supports single PDF or batch (directory of PDFs).
---

## Pipeline Flow

```
PDF
 ↓ MinerU
{stem}.md  ← raw state, directly in collection folder
 ↓ LLM Cleanup (works in /tmp only, overwrites {stem}.md)
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

## Naming Convention

Collection name MUST be descriptive: `Qwen3_Embedding_Paper`, `SPLADE_Architecture`, `RAG_Survey_2024`

- NEVER use ArXiv IDs (`2506.05176`) or cryptic identifiers
- Format: PascalCase_With_Underscores, no spaces
- If the PDF filename is cryptic and no title is passed as argument, read the first page or the arxiv abstract to derive a descriptive name

**Data paths (CRITICAL):**
- All data writes go to the SOURCE repo: `~/Documents/ai/Meta/ClaudeCode/MCP/RAG/data/documents/`
- NEVER write to `${CLAUDE_PLUGIN_ROOT}/data/...` — those writes are lost on plugin-sync

---

## Phase 1: PDF to Markdown

### Step 1: Validate Input

```bash
ls -la "$PDF_PATH"
```

If not found, report error and stop.

### Step 2: Create Document Folder

```bash
STEM="<descriptive_name>"
mkdir -p ~/Documents/ai/Meta/ClaudeCode/MCP/RAG/data/documents/$STEM
```

### Step 3: Run MinerU Workflow

```bash
cd ${MINERU_PATH} && \
./venv/bin/python workflow.py convert \
  --input "$PDF_PATH" \
  --output ~/Documents/ai/Meta/ClaudeCode/MCP/RAG/data/documents/$STEM/$STEM.md
```

Output: `{stem}.md` = MinerU output + generic postprocess.py cleanup (raw state, directly in collection folder)

### Step 4: Verify

```bash
ls -la ~/Documents/ai/Meta/ClaudeCode/MCP/RAG/data/documents/$STEM/
```

### Phase 1 Report

```
PHASE 1: PDF to Markdown
========================
INPUT:  [PDF path]
OUTPUT: data/documents/$STEM/$STEM.md  (raw state)
STATUS: [Success/Failed]
```

---

## Phase 2: LLM Cleanup

Read `{stem}.md` (raw state), fix artifacts via scripts in `/tmp/`, overwrite `{stem}.md` with the clean version.

### PDF Cleanup Protocol

#### CRITICAL EXECUTION PROTOCOL

1. **FRESH SCRIPTS ONLY:** Always create NEW scripts in `/tmp/` named `/tmp/fix_{issue}_{stem}.py` where `stem = Path(input_file).stem`. Example: for `modulhandbuch_bwl.md` → `/tmp/fix_umlauts_modulhandbuch_bwl.py`. Never write scripts into the collection folder.
2. **PYTHON FOR METRICS:** Do NOT use Bash variables for word counting. Use simple `wc -w "file"` or a Python script.
3. **LANGUAGE AWARENESS:** Check document language first (German/English). Apply language-specific OCR fixes.
4. **DUPLICATE DETECTION:** Check for OCR duplicate headers:
   - Pattern: Line N is garbage run-on, Line N+1 is correct
   - Action: DELETE the garbage line completely
5. **DIAGNOSE FIRST:** Use regex that tolerates spaces (fuzzy matching for OCR artifacts)
6. **ONE SCRIPT PER ISSUE:** Separate scripts for each issue type
7. **ITERATE:** Fix one category at a time, verify word count after EACH
8. **NO COLLECTION POLLUTION:** NEVER create subfolders (`debug/`, `raw/`, `tmp/`) inside the collection folder. All process artifacts go to `/tmp/`.

#### Spaced Artifacts to Detect

- LaTeX: `\ f r a c`, `\ s u m`, `\ m a t h r m`
- Images: `! [ ] ( ... )` with spaces between chars
- Split words: "mod els", "alg orithm"

#### Task Requirements

1. Fix safe artifacts (LaTeX unwrap, broken images, encoding, HTML entities)
2. Conservative paragraph merge: Only merge hyphenated line-end splits
3. Dictionary-based word healing: Load `/usr/share/dict/words` OR build vocabulary from document

#### Validation Requirements (MANDATORY)

1. Capture word count BEFORE and AFTER
2. Word count must be stable (+/- 1%)
3. Check for run-on words (iscentral, tothe, ofthe)
4. If word count drops >2% or run-on words found: ABORT and report

#### Workflow

1. **Diagnose:** Scan for all issue types (broken_images, encoding, split_words, etc.)
2. **Backup:** `cp "{input_file}" "/tmp/backup_{stem}.md"` — do this BEFORE any modification. If a fix goes wrong, restore via `cp /tmp/backup_{stem}.md "{input_file}"`.
3. **Fix Loop:** For each issue type, create `/tmp/fix_{issue_type}_{stem}.py`, run, verify count reaches 0
4. **Report:** Per-issue counts (before -> after), scripts created, final status

#### Output Format

```
ISSUES FOUND:
- [issue_type]: [count] occurrences

FIXES APPLIED:
- [issue_type]: [before] -> [after] ([script_name])

WORD COUNT: [before] -> [after] ([+/- %])
STATUS: [CLEAN / ISSUES_REMAINING / ABORTED]
```

### Verify Cleanup

**CRITICAL:** Verify your own cleanup independently before proceeding.

1. **Grep for claimed fixes** — For each pattern claimed fixed, grep BOTH raw and clean file:
   - Raw file must show matches (confirms pattern existed)
   - Clean file must show 0 matches (confirms fix applied)
2. **Stichprobe Content** — Read 10-15 lines from the middle of both files side-by-side, confirm no content loss beyond the fixes
3. **Line count** — Compare `wc -l` of raw vs clean. Should be stable (equal or very close)

Report verification result in table format:

```
| Pattern | Raw | Clean | Status |
|---------|-----|-------|--------|
| [pattern] | N matches | 0 matches | OK/FAIL |
```

If any FAIL → report and stop.

### Phase 2 Report

```
PHASE 2: LLM Cleanup
=====================
ISSUES FOUND:    [list]
FIXES APPLIED:   [list with counts]
WORD COUNT:      [before] -> [after] ([+/- %])
VERIFICATION:    [table]
STATUS:          [CLEAN / ISSUES_REMAINING / ABORTED]
```

---

## Phase 3: Chunk + Index

### Data Model

```
collection = folder name (e.g. "Qwen3_Embedding_Paper")
document   = file name (e.g. "Qwen3_Embedding_Paper.md")
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

### Phase 3 Report

```
PHASE 3: Chunk + Index
=======================
CHUNKS INDEXED: [N]
VERIFIED:       [Yes/No]
STATUS:         [Success/Failed]
```

---

## Batch Mode

When the caller passes a directory of PDFs (e.g. `data/pdf/<project>/`), run the full pipeline for each PDF sequentially and index all into a single collection.

**Invocation pattern:**

```
Input root:  data/pdf/<project>/           # directory containing *.pdf files
Output root: data/documents/<project>_reference/   # one folder = one collection
Collection:  <project>_reference           # derived from output root folder name
```

**Example:**

```
Input root:  data/pdf/RAG/
Output root: data/documents/RAG_reference/
Collection:  RAG_reference
```

### Batch Workflow

1. **List PDFs:**
   ```bash
   ls data/pdf/<project>/*.pdf
   ```

2. **For each PDF**, derive a descriptive PascalCase name:
   - Read first page or arxiv abstract (via CLI or embedded title)
   - Derive: e.g. `Attention_Is_All_You_Need`, `SPLADE_Architecture`

3. **Run Phase 1 (MinerU)** for that PDF, outputting to:
   ```bash
   ~/Documents/ai/Meta/ClaudeCode/MCP/RAG/data/documents/<project>_reference/<DescriptiveName>.md
   ```

4. **Run Phase 2 (LLM Cleanup)** on the generated .md file

5. **Run Phase 3 (index-dir)** pointing at the shared output root:
   ```bash
   cd ~/Documents/ai/Meta/ClaudeCode/MCP/RAG && \
   ./venv/bin/python workflow.py index-dir \
     --input data/documents/<project>_reference/ \
     --collection <project>_reference
   ```
   (Running index-dir once per PDF is fine — it is incremental and only re-indexes changed documents)

6. **Report** per-PDF status, then a batch summary when all PDFs are processed:

```
BATCH SUMMARY
=============
Total PDFs:     [N]
Indexed:        [N]
Failed:         [N]
Collection:     <project>_reference
Chunks total:   [N]
```

### Single-PDF Invocation Example

```
Skill(skill="pdf-convert")
Arguments: PDF=/path/to/paper.pdf STEM=Qwen3_Embedding_Paper
```

### Batch Invocation Example

```
Skill(skill="pdf-convert")
Arguments: PDF_DIR=data/pdf/RAG/ OUTPUT_ROOT=data/documents/RAG_reference/
```
