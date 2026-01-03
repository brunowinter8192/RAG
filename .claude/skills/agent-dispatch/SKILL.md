---
name: agent-dispatch
description: (project)
---

# Agent Dispatch

## Agent Registry

| Agent | Model | Purpose | Output |
|-------|-------|---------|--------|
| code-investigate-specialist | Haiku | Codebase exploration, file search | FILE/LINES/RELEVANT |
| md-cleanup-master | Haiku | Clean PDF-converted markdown | Issues found, fixes applied, line count |

---

## General Rules (All Agents)

### Script Location

Agents may create scripts during their work. All scripts go to:
```
{project_root}/debug/
```

This folder is gitignored and exempt from code standards.

### Parallel Agent Rules

Parallel agents are only efficient with **disjoint datasets**.

**Partition by:**
- **Layer:** Agent A = Docs only, Agent B = Code only
- **Scope:** Agent A = Training/, Agent B = Evaluation/
- **Aspect:** Agent A = Input/Output flow, Agent B = Algorithm logic

**NEVER:** Have multiple agents read the same files.

---

## code-investigate-specialist

### When to Use

**Simple Rule:**
- **User provides file path** → Read directly (no agent)
- **User provides directory path** → Use agent (content unknown)

**Better one agent too many than one too few.**

Use agent when:
- User gives directory instead of file
- "Where is X?" / "How does Y work?" questions
- Comparing between directories
- Searching >3 unknown files

Do NOT use agent when:
- User provides exact file path
- Reading single known files
- Targeted grep/glob with clear scope

### How to Prompt

**BAD:**
- "Find where features are defined"
- "How does pattern selection work?"
- "List all subdirectories and their contents" (too broad)

**GOOD:**
- "Find FEATURES constant definition in Runtime_Prediction/"
- "Find function that filters patterns by MRE threshold in 10_Pattern_Selection/"
- "List subdirectories and Python files in Misc/. Exclude csv/, data files."

**Pattern:**
1. Specific target (constant, function, class)
2. Scope (directory)
3. Constraints: "Exclude *.csv, *.png" or "Limit depth to 2"
4. Context if needed
5. **Follow imports:** "If code imports from external modules, locate and READ those files"

### After Agent Returns

**MANDATORY VERIFICATION GATE**

**BEFORE you write ANY response to user:**

1. **READ** at least 1 critical file mentioned by agent
2. **VERIFY** key claims (file exists, path correct, function does X)
3. **ONLY THEN** report to user

**NO EXCEPTIONS.** Agent = Scout, not Authority.

Agent may:
- Miss files
- Misinterpret code
- Hallucinate paths

**If you catch yourself about to respond without verification:**
- STOP
- Read at least 1 file first
- OR state explicitly: "Agent output not verified"

---

## md-cleanup-master

### When to Use

After PDF-to-markdown conversion when postprocess.py has run but semantic issues remain.

### How to Prompt

**Goal: Clean artifacts but PRESERVE content integrity.**
It is better to leave a split word unfixed than to merge two separate words.

```
Clean up the raw markdown file produced from a PDF conversion.

INPUT: {input_filepath}
OUTPUT: {output_filepath}

**CRITICAL EXECUTION PROTOCOL:**
1. **FRESH SCRIPTS ONLY:** Do NOT reuse existing scripts in `debug/`. Always create NEW scripts named `debug/fix_{issue}_{stem}.py`. Old scripts may have different logic.
2. **PYTHON FOR METRICS:** Do NOT use Bash variables for word counting (`VAR=$(wc -w...)` fails with spaces in filenames). Use simple `wc -w "file"` or a Python script.
3. **LANGUAGE AWARENESS:** Check document language first (German/English). Apply language-specific OCR fixes (e.g., `fir`→`für` in German, `5O`→`50`).
4. **DUPLICATE DETECTION:** Check for OCR duplicate headers:
   - Pattern: Line N is garbage run-on (`HOWNETWORKEDMARKETS`), Line N+1 is correct (`# HOW NETWORKED MARKETS...`)
   - Action: DELETE the garbage line completely (do not try to fix it)
5. **DIAGNOSE FIRST:** Use regex that tolerates spaces (fuzzy matching for OCR artifacts)
6. **ONE SCRIPT PER ISSUE:** Separate scripts for each issue type (fix_latex.py, fix_images.py, etc.)
7. **ITERATE:** Fix one category at a time, verify word count after EACH

**Spaced Artifacts to detect (OCR splits characters):**
- LaTeX: `\ f r a c`, `\ s u m`, `\ m a t h r m`
- Images: `! [ ] ( ... )` with spaces between chars
- Split words: "mod els", "alg orithm"

**Task Requirements:**
1. **Fix safe artifacts:**
   - LaTeX: **UNWRAP** arguments, do not delete them
     (e.g., `\textbf{foo}` -> `foo`, NOT empty string)
     Only delete standalone command names without arguments.
   - Images: Remove broken references.
   - Encoding: Replace corrupted characters.
   - HTML entities: Decode to plain text.
2. **Conservative paragraph merge:** Only merge hyphenated line-end splits
3. **Dictionary-based word healing:**
   - **MANDATORY:** Do NOT use a hardcoded list of ~50 words.
   - Load `/usr/share/dict/words` OR build vocabulary from
     the document itself (all words length > 3).
   - Merge split words only if result is in comprehensive vocabulary.

**Validation Requirements (MANDATORY):**
1. Capture word count BEFORE and AFTER
2. Word count must be stable (+/- 1%)
3. Check for run-on words (iscentral, tothe, ofthe)
4. If word count drops >2% or run-on words found → ABORT

**Success Metric:**
- ZERO run-on words (no "iscentral", "toeffective")
- Word count STABLE (+/- 1%) ← KEY METRIC
- Report: "patterns found" vs "patterns fixed" (145 found, 2 fixed = SUCCESS)
- Fixing few real artifacts while skipping valid grammar = CORRECT behavior
```

**With known issues (faster):**
```
Known issues:
- OCR: [describe specific patterns found]
- LaTeX: [describe remnants]
```

### What Agent Does

1. Diagnose: Scan for all issue types (broken_images, encoding, split_words, etc.)
2. Fix Loop: For each issue type, create `debug/fix_{issue_type}.py`, run, verify → 0
3. Report: Per-issue counts (before → after), scripts created, final status

### Iteration

If remaining issues after first run:
- Re-run agent with same prompt
- Agent analyzes remaining issues, extends relevant fix scripts
- Repeat until all issue counts → 0

### After Agent Returns

1. **Word count check:** Compare input vs output word count (must be stable +/- 1%)
2. **Run-on word check:** `grep -oE '\b(isthe|tothe|ofthe|inthe|iscentral)\b' {cleaned_file}`
3. If run-on words found → re-run agent (iteration) or manual fix
4. If word count stable AND no run-on words → done
