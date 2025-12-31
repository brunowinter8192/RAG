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

**CRITICAL CONSTRAINTS (always include):**
```
Clean the PDF-converted markdown at {filepath}

EXISTING SCRIPT: debug/clean_{name}.py exists from last session. Use and extend it if needed.
(Or: No existing script. Create new one.)

SAFETY CONSTRAINTS:
1. Before ANY changes: verify line count (wc -l). After changes: check again.
   If line count drops >1%, REVERT immediately (git checkout).
2. Do NOT read full file (>250KB). Use grep -nC 3 to inspect patterns locally.
3. Regex MUST be surgical: use word boundaries (\bpattern\b).
   NEVER use greedy wildcards (.*) that span lines.
4. After cleanup: verify structural syntax intact (operators, keywords preserved).

OUTPUT: {output_filepath}
```

**With known issues (faster):**
```
Known issues:
- OCR: [describe specific patterns found, e.g., "1/l confusion in identifiers"]
- LaTeX: [describe remnants, e.g., "mathbf, prime symbols"]
- Structure: [describe structural issues, e.g., "broken table aliases"]
```

**Pattern for prompting:**
1. Always include SAFETY CONSTRAINTS block
2. Mention existing script if one exists (agent extends it)
3. Add known issues if available (skips discovery phase)
4. Specify output filename

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
