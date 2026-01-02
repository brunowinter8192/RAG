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

**CRITICAL: Define cleanup scope explicitly**

```
Clean up the raw markdown file produced from a PDF conversion.

INPUT: {input_filepath}
OUTPUT: {output_filepath}

**Task Requirements:**
1. **Merge broken paragraphs:** Identify sentences split across lines (hard wraps)
   and merge them into single paragraphs. Line count MUST DROP significantly.
2. **Fix OCR artifacts:** Correct split words ('mod els'), broken hyphens
   ('learning- based'), encoding errors ('Ð', 'ˇ').
3. **Remove broken elements:** Empty image refs `![](images/.jpg)`, LaTeX remnants.

**Success Metric:**
- Paragraphs flow as continuous text (no newlines mid-sentence)
- Pattern counts (broken words, encoding, broken lines) drop to near-zero
- Report: "artifact_type: X -> Y" for each type found

EXISTING SCRIPT: ./debug/clean_{name}.py
(Check if exists, use and extend if so)
```

**With known issues (faster):**
```
Known issues:
- OCR: [describe specific patterns found, e.g., "1/l confusion in identifiers"]
- LaTeX: [describe remnants, e.g., "mathbf, prime symbols"]
- Structure: [describe structural issues, e.g., "broken table aliases"]
```

### What Agent Does

1. Check if `debug/clean_{name}.py` exists
2. Sample file with `head`/`sed -n` to understand structure
3. If script exists → analyze remaining issues → extend script
4. If not → create new cleanup script
5. Run script → outputs `{file}_cleaned.md`
6. Verify with `grep`/`diff`
7. Report: issues found, fixes applied, output file path

### Iteration

If remaining issues after first run:
- Re-run agent with same prompt
- Agent analyzes remaining issues
- Agent extends its OWN script (never manual extension)
- Repeat until clean

### After Agent Returns

1. Spot check: `grep -c "{patterns_from_known_issues}" {cleaned_file}`
2. If count > 0 → re-run agent (iteration)
3. If count = 0 → done, move cleaned file to final location
