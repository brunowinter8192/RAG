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

**Einfache Regel:**
- **File-Pfad vom User** → Direkt lesen (kein Agent)
- **Directory-Pfad vom User** → Agent (Inhalt unbekannt)

**Besser einen Agent zu viel als einen zu wenig.**

Use agent when:
- User gibt Directory statt File
- "Wo ist X?" / "Wie funktioniert Y?" Fragen
- Vergleiche zwischen Directories
- >3 unbekannte Files durchsuchen

Do NOT use agent when:
- User gibt exakten File-Pfad
- Einzelne bekannte Files lesen
- Gezielte Grep/Glob mit klarem Scope

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

**Tool Recommendations:**
- "Use `find` to locate files. Do NOT use `ls -R`"
- For CSV value search: "Use awk for numeric comparison, not grep"
- For large result sets: "Count matches first before printing"

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
- OR state explicitly: "Agent-Output nicht verifiziert"

### Known Pitfalls

**1. Path Hallucinations**
- **Symptom:** `Tool_use_error: File does not exist`
- **Fix in prompt:** "Only read files explicitly listed in your previous `find` or `ls` output"

**2. Serial Reads (Latency)**
- **Symptom:** Multiple sequential Read calls for related files
- **Fix in prompt:** "Read related config files in a single step when possible"

**3. Missing File Chase**
- **Symptom:** 5+ attempts to find a file that doesn't exist
- **Fix in prompt:** "If a referenced file is missing after 2 search attempts, log as 'MISSING: <file>' and continue"

**4. Redundant grep + read**
- **Symptom:** grep output followed by full file read
- **Fix in prompt:** "Use grep with `-C 5` context. Only read full file if context is insufficient"

---

## md-cleanup-master

### When to Use

After PDF-to-markdown conversion when postprocess.py has run but semantic issues remain.

### How to Prompt

**Minimal:**
```
Clean the PDF-converted markdown at {filepath}
```

**With context (faster - agent skips discovery):**
```
Clean the PDF-converted markdown at {filepath}

Known issues:
- OCR: 0/o and 1/l confusion in identifiers
- Dates: Format issues like YYYY.MM-DD
- LaTeX remnants
```

If you have prior knowledge about the document's issues, include them. Agent will skip discovery phase.

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

1. Spot check: `grep -c "0_\|1_\|\\\\mathbf" {cleaned_file}`
2. If count > 0 → re-run agent (iteration)
3. If count = 0 → done, rename/move cleaned file
