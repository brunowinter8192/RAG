---
name: agent-dispatch
description: (project)
---

# Agent Dispatch

## Agent Registry

| Agent | Model | Purpose | Output |
|-------|-------|---------|--------|
| code-investigate-specialist | Haiku | Codebase exploration, file search | FILE/LINES/RELEVANT |

## CRITICAL: Default Behavior

**When this skill is active:**
1. ALL codebase exploration → code-investigate-specialist
2. NEVER use Explore subagent type directly
3. NEVER do manual Glob/Grep chains when Agent can do it

**If you catch yourself typing `subagent_type=Explore`:**
→ STOP
→ Use `subagent_type=code-investigate-specialist` instead

## How to Prompt

**BAD:**
- "Find where features are defined"
- "How does pattern selection work?"
- "List all subdirectories and their contents" (too broad, causes context pollution)

**GOOD:**
- "Find FEATURES constant definition in Runtime_Prediction/"
- "Find function that filters patterns by MRE threshold in 10_Pattern_Selection/"
- "List subdirectories and Python files in Misc/. Exclude csv/, data files."

**Pattern:**
1. Specific target (constant, function, class)
2. Scope (directory)
3. Constraints: "Exclude *.csv, *.png" or "Limit depth to 2"
4. Context if needed (what you already know)
5. **Follow imports:** "If code imports from external modules, locate and READ those files"

**Exploration Constraints:**
- Always specify: "Exclude data files (*.csv, *.png, *.jpg)"
- For unknown directories: "Limit initial depth to 2 levels"
- For doc audits: "Focus on *.py files and DOCS.md"

**Tool Recommendations:**
- "Use `find` to locate files. Do NOT use `ls -R`"
- For CSV value search: "Use awk for numeric comparison, not grep"
- For large result sets: "Count matches first before printing"

## When to Use Agent

**Einfache Regel:**
- **File-Pfad vom User** → Direkt lesen (kein Agent)
- **Directory-Pfad vom User** → Agent (Inhalt unbekannt)

**Besser einen Agent zu viel als einen zu wenig.**

Use agent when:
- User gibt Directory statt File
- "Wo ist X?" / "Wie funktioniert Y?" Fragen
- Vergleiche zwischen Directories (z.B. Hybrid_2 vs Online_1)
- >3 unbekannte Files durchsuchen

Do NOT use agent when:
- User gibt exakten File-Pfad
- Einzelne bekannte Files lesen
- Gezielte Grep/Glob mit klarem Scope

## Parallel Agent Rules

Parallel agents are only efficient with **disjoint datasets**.

**Partition by:**
- **Layer:** Agent A = Docs only, Agent B = Code only
- **Scope:** Agent A = Training/, Agent B = Evaluation/
- **Aspect:** Agent A = Input/Output flow, Agent B = Algorithm logic

**NEVER:** Have multiple agents read the same files.

**BAD:**
- Agent A: "Investigate Runtime_Prediction/"
- Agent B: "Investigate Online_1/"
→ Both read workflow.py, DOCS.md, selection.py = wasted tokens

**GOOD:**
- Agent A (Architect): "Read ONLY DOCS.md and src/DOCS.md - create module map"
- Agent B (Inspector): "Read ONLY src/*.py - analyze selection logic"
→ Disjoint datasets, merge results in main agent

## After Agent Returns

⛔ **MANDATORY VERIFICATION GATE** ⛔

**BEFORE you write ANY response to user:**

1. **READ** at least 1 critical file mentioned by agent
2. **VERIFY** key claims (file exists, path correct, function does X)
3. **ONLY THEN** report to user

**NO EXCEPTIONS.** Agent = Scout, not Authority.

Agent provides:
- WHERE: File + lines
- HOW: Its interpretation (may be wrong)

Agent may:
- Miss files
- Misinterpret code
- Hallucinate paths

**If you catch yourself about to respond without verification:**
→ STOP
→ Read at least 1 file first
→ OR state explicitly: "⚠️ Agent-Output nicht verifiziert"

## Known Agent Pitfalls

### 1. Path Hallucinations
Agent guesses paths instead of using `find` output.
- **Symptom:** `Tool_use_error: File does not exist`
- **Fix in prompt:** "Only read files explicitly listed in your previous `find` or `ls` output"

### 2. Serial Reads (Latency)
Agent reads files one-by-one instead of batching.
- **Symptom:** Multiple sequential Read calls for related files
- **Fix in prompt:** "Read related config files (makefile, headers) in a single step when possible"

### 3. Missing File Chase
Agent spends many steps searching for referenced but non-existent files.
- **Symptom:** 5+ attempts to find a file that doesn't exist
- **Fix in prompt:** "If a referenced file is missing after 2 search attempts, log as 'MISSING: <file>' and continue"

### 4. Redundant grep + read
Agent greps, then reads entire file anyway.
- **Symptom:** grep output followed by full file read
- **Fix in prompt:** "Use grep with `-C 5` context. Only read full file if context is insufficient"

### 5. C-Code Pattern Blindness
Simple text search misses array/struct definitions.
- **Symptom:** "Not found" when values exist in arrays like `defaults[][]`
- **Fix in prompt:** "Note: TPC-H/C code stores parameters in static arrays (e.g., `defaults[][]`), not individual constants"
