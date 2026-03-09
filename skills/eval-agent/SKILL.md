# Eval Agent Skill

Evaluate subagent sessions: index into RAG, analyze tool usage, propose automation file improvements, cleanup.

**FIRST:** Activate Skill('rag:RAG') for correct RAG MCP tool usage.

Input: $ARGUMENTS
Format: `<project_path>` or `<project_path> <count>` or `<project_path> session`

PLUGIN_DIR: the RAG plugin root (resolve via `~/.claude/plugins/cache/brunowinter-plugins/rag/1.0.0`)
ITERDEV_DIR: `~/.claude/plugins/cache/brunowinter-plugins/iterative-dev/1.0.0`

---

## CRITICAL RULES

### Stop on Error (NON-NEGOTIABLE)

If ANY step fails (JSONL conversion, chunking, indexing, RAG tool call):
- **STOP IMMEDIATELY**
- Report the exact error message
- Do **NOT** proceed with workarounds ("I'll read the files directly")
- Do **NOT** skip the failed agent and continue with the next
- Do **NOT** invent alternative approaches

### Agent Loop (NON-NEGOTIABLE)

When multiple agents are selected for evaluation:
- Process ALL selected agents, not just the first one
- For EACH agent: execute Phases 2-6 completely before starting the next
- After finishing one agent, explicitly state: "Agent N/M done. Starting next agent."

### Non-Interactive Mode

When the prompt contains "Non-interactive" or "write reports to":
- Write evaluation reports to the specified directory (usually `<project_path>/Evaluation_Proposals/`)
- File naming: `eval-<agent_id>-<agent_type_short>.md`
- Do NOT present findings interactively — write the full report to file
- Do NOT ask for user input at any point

---

## Phase 1: Find Subagent

### 1.1 Session JSONL Location

Session JSONLs are written **dynamically** during the session (not only at session end). The active session's JSONL is always available.

CC projects directory: `~/.claude/projects/<escaped-project-path>/`
- `<escaped-project-path>` = absolute project path with `/` replaced by `-` (leading `/` becomes `-`)
- Example: `/Users/foo/MyProject` → `-Users-foo-MyProject`

**Find the newest session (= the active one):**
```bash
ls -t ~/.claude/projects/<escaped-project-path>/*.jsonl | head -1
```

**Find subagents of that session:**
```bash
SESSION_DIR=$(ls -td ~/.claude/projects/<escaped-project-path>/*/ | head -1)
ls $SESSION_DIR/subagents/
```

### 1.2 List Agents

1. Run list_agents.py to get all subagents with their types:
   ```bash
   # All agents:
   cd $ITERDEV_DIR && python3 -m src.pipeline.list_agents --project <project_path>
   # Latest session only:
   cd $ITERDEV_DIR && python3 -m src.pipeline.list_agents --project <project_path> --session latest
   ```
   This outputs: agent_id, agent_type, timestamp, size (sorted newest first).

   **If list_agents.py fails** (e.g., "Main session not found"): The script derives the main session JSONL from the subagent path. If the JSONL doesn't exist yet or the session directory is stale, use the manual approach from 1.1 to identify the correct session, then pass specific subagent paths directly to Phase 2.

2. Present the table to user (or select automatically in non-interactive mode)
3. If `session` was given: use `--session latest` flag, take all agents from most recent session
4. If `<count>` was given: take the N most recent from today's date, no user selection needed
5. If user says "the newest" or similar: take the single most recent from today's date
6. Otherwise: ask user which subagent(s) to evaluate
7. For the selected agent(s), get the JSONL path:
   `~/.claude/projects/<escaped-project-path>/*/subagents/agent-<agent_id>.jsonl`

---

## Phase 2: JSONL to MD, Chunk, Index

For each selected subagent:

```bash
# Convert JSONL to MD with dispatch context (produces TWO files)
# <agent_id>.md = tool call details only (for RAG)
# <agent_id>_summary.md = dispatch context + task prompt + tool call summary + final response (for Read tool)
cd $ITERDEV_DIR && python3 -m src.pipeline.jsonl_to_md \
    --input "<jsonl_path>" --output "$PLUGIN_DIR/data/documents/Subagents/<agent_id>.md" --dispatch

# Chunk (only the details file, NOT the summary)
$PLUGIN_DIR/venv/bin/python $PLUGIN_DIR/workflow.py chunk \
    --input "$PLUGIN_DIR/data/documents/Subagents/<agent_id>.md" --chunk-size 1000 --overlap 200

# Index
$PLUGIN_DIR/venv/bin/python $PLUGIN_DIR/workflow.py index-json \
    --input "$PLUGIN_DIR/data/documents/Subagents/<agent_id>.json"
```

**If any command fails: STOP. Report error. Do not continue.**

**Embedding Server Crash Recovery:**
If indexing fails with connection errors (port 8081 refused, timeout), the embedding server has crashed. Auto-start does NOT work from the plugin cache (llama.cpp binary not present). Inform the user immediately: "Embedding server is down. Please restart it manually, then I'll retry the indexing step."

---

## Phase 3: Read & Evaluate

### 3.1 Read Session Overview

Use the **Read tool** (NOT RAG) to read the summary file directly:

```
Read $PLUGIN_DIR/data/documents/Subagents/<agent_id>_summary.md
```

This gives the complete overview in one call:
- Dispatch Context (pre-dispatch messages, dispatch prompt, post-dispatch)
- Task Prompt
- Tool Call Summary — each line shows: `[HH:MM:SS] #N tool_name: key=value, key=value  [size chars]`
  This reveals HOW the agent used its tools (which parameters it chose, in what order, at what timestamps)
- Final Response

### 3.2 Systematic Tool Call Reading

The summary shows parameters and output SIZES, not content. The actual tool call details are in RAG.

**Use RAG tools** (following the activated RAG Skill) to read tool call details:

```
mcp__plugin_rag_rag__read_document(collection="Subagents", document="<agent_id>.md", start_chunk=0, num_chunks=10)
```

**MANDATORY:** Read the actual tool call outputs for:
- All calls with large outputs (>1000 chars) — these contain the real findings
- All calls with small outputs (<400 chars) — verify if empty/error/short result
- Calls where the agent changed strategy — read what triggered the change
- The last 3 calls before the final response — understand what led to the conclusion

Continue reading chunks until you have covered ALL tool call sections.

### 3.3 Evaluate

Present findings to user interactively (or write to report in non-interactive mode).

#### What Went Well
For each positive:
- **What:** Concrete observation
- **Why it matters:** What this prevented or enabled

#### What Went Wrong
For each problem:
- **What:** Concrete observation
- **Why:** Root cause — trace to the automation file rule that was violated or missing
- **Evidence:** Exact quote from agent output or tool call

**Inconsistency check (MANDATORY):**
When an agent uses a parameter correctly in SOME calls but not others (e.g., `limit=300` on one file but reads 44KB without limit on another):
- Flag this as STRONGER evidence than complete absence — it proves the agent KNOWS the parameter but applies it inconsistently
- Include both the correct and incorrect usage as evidence in the proposal
- This pattern suggests the agent definition needs a RULE, not just a hint

**Dispatch errors ARE automation file problems (MANDATORY):**
Every dispatch problem traces to a Skill section that controls prompt construction. NEVER dismiss dispatch errors as "one-off" or "not fixable via automation files."

#### Dispatch Quality
- Was the task prompt precise enough?
- Did the sub receive all necessary context?
- Did the main agent meaningfully use the sub's response?
- Did dispatch quality cause any of the sub's failures?

**Dispatch problems MUST produce proposals (NON-NEGOTIABLE):**
When you identify a dispatch problem (contradictory instructions, missing context, wrong format request):
- Do NOT just say "this is a dispatch problem, not an agent problem"
- ALWAYS propose a concrete fix for the dispatcher's Skill (e.g., iterative-dev SKILL.md dispatch section)
- The proposal targets the SKILL that controls how the main agent constructs dispatch prompts
- Example: "Don't mix content-understanding questions with locate-only output format in the same dispatch"

#### Model-Specific Patterns
Based on the model used:
- **Haiku:** Format drift, scope creep, path hallucinations, stop criteria ignored
- **Sonnet/Opus:** Over-engineering, unnecessary verbosity

---

## Phase 4: Read Automation Files

### 4.1 Identify Plugin

Match agent name to plugin:

| Agent | Plugin | Model |
|-------|--------|-------|
| github-search | github-research | Haiku |
| reddit-search | reddit | Haiku |
| code-investigate-specialist | iterative-dev | Haiku |
| web-research | searxng | Haiku |
| git-committer | iterative-dev | Haiku |

### 4.2 Locate Plugin Source

```bash
find ~/.claude/plugins/cache/brunowinter-plugins/ -name "plugin.json" | head -10
```

Read the plugin.json to find paths for agent definition + skills.

### 4.3 Read Automation Files

Read ALL relevant files using the Read tool:
- Agent definition (agents/<name>.md)
- Agent skill (skills/agent-<name>/SKILL.md)
- Domain skill (skills/<domain>/SKILL.md)

These are the targets for improvement proposals. You MUST read them BEFORE writing any proposals in Phase 5.

**Read Before Proposing (CRITICAL):** Proposals that contradict existing rules in the target file waste everyone's time. Reading the target file first prevents this.

**Plugin-Scope Rule:** Proposals target the plugin that OWNS the agent:
- Global agents (code-investigate-specialist, git-committer) -> iterative-dev plugin source
- Project-scoped agents (github-search, reddit-search, web-research) -> their respective plugin source repo
- Edits go in the plugin SOURCE repo, not in the cache

---

## Phase 5: Proposals & Report

### 5.1 Root Cause Analysis

| Problem | Symptom | Root Cause | Automation File |
|---------|---------|------------|-----------------|
| ... | ... | ... | ... |

### 5.2 Concrete Proposals

For EACH identified problem, propose a change:

```
### Proposal N: [Title]

**File:** [Full path to automation file]
**Location:** [Section name]

**WHY:** [Root cause]

**Current:**
[Exact current text from the file]

**Proposed:**
[Exact replacement text]

**Expected Impact:** [Concrete improvement]
```

CRITICAL:
- Every proposal MUST have a WHY
- Current text MUST be the actual text from the file (quoted exactly)
- Proposals target automation files (Skills, Agent definitions, Commands), NOT application code
- **No contradictions:** Verify the proposal does not conflict with existing rules in the same file or in `~/.claude/CLAUDE.md`
- **Cost awareness:** Dispatcher = Opus, Sub = Haiku. An Opus verification call may cost MORE than the sub's error recovery. Prefer giving the sub better self-recovery instructions over adding Opus pre-checks.
- **Simplicity rule for sub-agent formats:** When your proposal introduces a new block format that a sub-agent must produce, check the agent's model in the Phase 4.1 table. For Haiku agents: maximum 2-3 fields per block (Haiku drifts with 4+ fields). Prefer extending existing formats over creating new ones. Wrong: `STRUCTURE: / COUNT: / METHOD: / RESULT:` (4 fields). Right: `TREE: / COUNT:` (2 fields). Test: Could the agent's model produce this format consistently after seeing ONE example?

### 5.3 Apply Proposals

**Interactive mode:** Apply proposals directly to the automation files after user approval.
**Non-interactive mode:** Write report to `<project_path>/Evaluation_Proposals/eval-<agent_id>-<agent_type_short>.md`. Do NOT apply changes.

---

## Phase 6: Cleanup

After proposals are written/applied:

```bash
# Delete from RAG
cd $PLUGIN_DIR && ./venv/bin/python workflow.py delete --collection Subagents --document <agent_id>.md

# Remove temp files (details + summary + chunks JSON)
rm -f $PLUGIN_DIR/data/documents/Subagents/<agent_id>.md
rm -f $PLUGIN_DIR/data/documents/Subagents/<agent_id>_summary.md
rm -f $PLUGIN_DIR/data/documents/Subagents/<agent_id>.json
```

Verify cleanup:
```
mcp__plugin_rag_rag__list_documents(collection="Subagents")
```

**Then proceed to next agent if more are queued.**
