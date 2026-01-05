---
name: agent-dispatch
description: (project)
---

# Agent Dispatch

## Structure

This skill is **MODULAR**:
- **General Rules** (this section) → Apply to ALL agents
- **Agent-Specific Sections** (below) → Only for that agent type

---

# General Rules (ALL Agents)

## When to Use Agents

**Rule of thumb:** Better one agent too many than one too few.

Use agent when:
- Exploration scope unclear
- Multiple sources to check
- >20k tokens of reading expected

Do NOT use when:
- Single file/URL (known path)
- Quick verification

## Parallel Agent Rules

Parallel agents are only efficient with **disjoint datasets**.

**Partition by:**
- **Layer:** Agent A = Docs only, Agent B = Code only
- **Scope:** Agent A = src/, Agent B = tests/
- **Aspect:** Agent A = Input/Output flow, Agent B = Algorithm logic

**NEVER:** Have multiple agents read the same files.

## After Agent Returns

**CRITICAL: Agent = Scout, not Authority**

Agent provides:
- WHERE: Location (file/URL)
- WHAT: Its interpretation

**You MUST:**
1. Present results directly to user (don't summarize the summary)
2. Verify critical findings yourself if needed
3. When in doubt: check yourself instead of trusting blindly

**NEVER** trust agent output blindly. The agent may:
- Miss files
- Misinterpret code
- Hallucinate paths

**Retry Logic:**
If results are useless (generic, wrong topic, no insights):
- Re-run with feedback: "Previous results were [problem]. This time: [fix]"
- Max 2 retries, then report failure to user

## Verification Checklist

Before reporting agent results to user:

- [ ] Read at least 1 critical file mentioned by agent
- [ ] Confirm key claims (file exists, function does X)
- [ ] If agent provided summary: spot-check 1-2 details

**If you skip verification:**
→ State explicitly: "Agent output not verified"

---

# code-investigate-specialist

## Agent Info

| Agent | Model | Purpose | Output |
|-------|-------|---------|--------|
| code-investigate-specialist | Haiku | Codebase exploration, file search | FILE/LINES/RELEVANT |

## When to Use

**Simple Rule:**
- **User provides file path** → Read directly (no agent)
- **User provides directory path** → Use agent (content unknown)

Use agent when:
- User gives directory instead of file
- "Where is X?" / "How does Y work?" questions
- Comparing between directories
- Searching >3 unknown files

Do NOT use agent when:
- User provides exact file path
- Reading single known files
- Targeted grep/glob with clear scope

## How to Prompt

**BAD:**
- "Find where features are defined"
- "How does pattern selection work?"
- "List all subdirectories and their contents" (too broad)

**GOOD:**
- "Find FEATURES constant definition in src/"
- "Find function that filters by threshold in selection/"
- "List subdirectories and Python files in Misc/. Exclude csv/, data files."

**Pattern:**
1. Specific target (constant, function, class)
2. Scope (directory)
3. Constraints: "Exclude *.csv, *.png" or "Limit depth to 2"
4. Context if needed
5. **Follow imports:** "If code imports from external modules, locate and READ those files"

**Exploration Constraints:**
- Always specify: "Exclude data files (*.csv, *.png, *.jpg)"
- For unknown directories: "Limit initial depth to 2 levels"
- For doc audits: "Focus on *.py files and DOCS.md"

## Tool Recommendations

Include in agent prompt:
- "Use `find` to locate files. Do NOT use `ls -R`"
- For CSV: "Use awk for numeric comparison, not grep"
- For JSON/JSONL: "Use jq or Python script. NEVER grep for field values."
- For large result sets: "Count matches first before printing"

## Known Agent Pitfalls

### 1. Path Hallucinations
Agent guesses paths instead of using `find` output.
- **Fix:** "Only read files explicitly listed in your previous `find` or `ls` output"

### 2. Serial Reads (Latency)
Agent reads files one-by-one instead of batching.
- **Fix:** "Read related config files in a single step when possible"

### 3. Missing File Chase
Agent spends many steps searching for non-existent files.
- **Fix:** "If a referenced file is missing after 2 search attempts, log as 'MISSING: <file>' and continue"

### 4. Redundant grep + read
Agent greps, then reads entire file anyway.
- **Fix:** "Use grep with `-C 5` context. Only read full file if context is insufficient"

### 5. Pattern Blindness
Simple text search misses array/struct definitions.
- **Fix:** "Note: Some codebases store parameters in static arrays, not individual constants"

---

# md-cleanup-master

## Agent Info

| Agent | Model | Purpose | Output |
|-------|-------|---------|--------|
| md-cleanup-master | Haiku | Clean PDF-converted markdown | Issues found, fixes applied, line count |

## When to Use

After PDF-to-markdown conversion when postprocess.py has run but semantic issues remain.

## Script Location

Agents may create scripts during their work. All scripts go to:
```
{project_root}/debug/
```
This folder is gitignored and exempt from code standards.

## How to Prompt

**Goal: Clean artifacts but PRESERVE content integrity.**
It is better to leave a split word unfixed than to merge two separate words.

```
Clean up the raw markdown file produced from a PDF conversion.

INPUT: {input_filepath}
OUTPUT: {output_filepath}

**CRITICAL EXECUTION PROTOCOL:**
1. **FRESH SCRIPTS ONLY:** Do NOT reuse existing scripts in `debug/`. Always create NEW scripts named `debug/fix_{issue}_{stem}.py`.
2. **PYTHON FOR METRICS:** Do NOT use Bash variables for word counting. Use simple `wc -w "file"` or a Python script.
3. **LANGUAGE AWARENESS:** Check document language first (German/English). Apply language-specific OCR fixes.
4. **DUPLICATE DETECTION:** Check for OCR duplicate headers (garbage line followed by correct line → DELETE garbage)
5. **DIAGNOSE FIRST:** Use regex that tolerates spaces (fuzzy matching for OCR artifacts)
6. **ONE SCRIPT PER ISSUE:** Separate scripts for each issue type
7. **ITERATE:** Fix one category at a time, verify word count after EACH

**Spaced Artifacts to detect:**
- LaTeX: `\ f r a c`, `\ s u m`, `\ m a t h r m`
- Images: `! [ ] ( ... )` with spaces between chars
- Split words: "mod els", "alg orithm"

**Validation Requirements (MANDATORY):**
1. Capture word count BEFORE and AFTER
2. Word count must be stable (+/- 1%)
3. Check for run-on words (iscentral, tothe, ofthe)
4. If word count drops >2% or run-on words found → ABORT
```

## Iteration

If remaining issues after first run:
- Re-run agent with same prompt
- Agent analyzes remaining issues, extends relevant fix scripts
- Repeat until all issue counts → 0

## After Agent Returns

1. **Word count check:** Compare input vs output word count (must be stable +/- 1%)
2. **Run-on word check:** `grep -oE '\b(isthe|tothe|ofthe|inthe|iscentral)\b' {cleaned_file}`
3. If run-on words found → re-run agent or manual fix
4. If word count stable AND no run-on words → done
