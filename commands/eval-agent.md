---
description: Evaluate any subagent session (index, analyze, propose improvements, cleanup)
argument-hint: <project-path>
---

# Subagent Evaluation

## Input

Project Path: $ARGUMENTS

---

## Phase 1: Find & Select Session

### Step 1: Encode Project Path

```bash
ENCODED=$(echo "$ARGUMENTS" | sed 's|/|-|g')
echo "Encoded project: $ENCODED"
```

### Step 2: List Subagent Sessions

```bash
find ~/.claude/projects/$ENCODED/*/subagents -name "agent-*.jsonl" 2>/dev/null | head -20
```

### Step 3: Present Options

List found sessions with numbers and timestamps.

**STOP** - Ask user: "Which subagent to evaluate? (number)"

---

## Phase 2: Index into RAG

### Step 1: Set Variables

```bash
AGENT_ID="<selected agent id from filename>"
JSONL_PATH="<full path to selected jsonl>"
OUTPUT_MD="${CLAUDE_PLUGIN_ROOT}/data/documents/Subagents/${AGENT_ID}.md"
```

### Step 2: Convert JSONL to Markdown

```bash
cd ${CLAUDE_PLUGIN_ROOT} && \
./venv/bin/python src/rag/jsonl_to_md.py \
    --input "$JSONL_PATH" \
    --output "$OUTPUT_MD" \
    --dispatch
```

### Step 3: Verify Conversion

```bash
head -50 "$OUTPUT_MD"
```

### Step 4: Chunk and Save as JSON

```bash
cd ${CLAUDE_PLUGIN_ROOT} && \
./venv/bin/python workflow.py chunk \
    --input "$OUTPUT_MD" \
    --chunk-size 1500 \
    --overlap 200
```

### Step 5: Index

```bash
cd ${CLAUDE_PLUGIN_ROOT} && \
./venv/bin/python workflow.py index-json --input data/documents/Subagents/${AGENT_ID}.json
```

**STOP** - Ask: "Session indexed. Proceed to evaluation?"

---

## Phase 3: Identify Agent & Load Automation Files

### Step 1: Extract Agent Info

From the indexed session, identify:
- **Agent name** (e.g., "github-search", "reddit-search", "code-investigate-specialist")
- **Model** (e.g., Haiku, Sonnet)

Read the task prompt directly (always Chunk 0):
```
mcp__rag__read_document(collection="Subagents", document="${AGENT_ID}.md", start_chunk=0, num_chunks=1)
```

### Step 2: Discover Plugin

Read the **Global Plugins** table in `~/.claude/CLAUDE.md`.

Match the agent name to its plugin:

| Agent | Plugin | Components |
|-------|--------|------------|
| github-search | github-research | gh-search Skill, github-search Agent, agent-github-search Skill |
| reddit-search | reddit | reddit Skill, reddit-search Agent, agent-reddit-search Skill |
| code-investigate-specialist | iterative-dev | iterative-dev Skill, code-investigate-specialist Agent, agent-code-investigate Skill |

### Step 3: Locate Plugin Source

```bash
find ~/.claude/plugins/cache/brunowinter-plugins/ -name "plugin.json" | head -10
```

Read the plugin.json for the identified plugin to find the source paths for:
- Agent definition (`.claude/agents/<name>.md`)
- Skills (`.claude/skills/<name>/SKILL.md`)

### Step 4: Load Automation Files

Read ALL identified Automation Files in parallel using the Read tool.

These are the files that control the agent's behavior — the targets for improvement proposals.

---

## Phase 4: Evaluate via RAG

### 4.1 Read Session Overview

Read dispatch context, task prompt, tool call summary, and final response:

```
mcp__rag__read_document(collection="Subagents", document="${AGENT_ID}.md", start_chunk=0, num_chunks=5)
```

This returns:
- **Dispatch Context** (Chunk 0-1): Main agent's reasoning before dispatch + how it processed the result
- **Task prompt** (Chunk ~2): What was the agent supposed to do?
- **Tool Call Summary** (Chunk ~3): All tool calls in sequence with output sizes
- **Final response** (Chunk ~4): What did the agent deliver?

### 4.2 Task Fulfillment (35%)

Extract requirements from task prompt. For each requirement:

| Requirement | Fulfilled? | Comment |
|-------------|-----------|---------|
| [Extract from task] | Yes/No/Partial | [What's missing/correct] |

### 4.3 Tool Efficiency (25%)

Analyze the **Tool Call Summary table** from 4.1. Look for:
- **Redundant calls:** Same path accessed via `find` then `ls` — one would suffice
- **Large outputs:** >2000 chars suggests agent read too much (missing `--exclude` or `limit`)
- **Wasted calls:** Tools called on out-of-scope files

For suspicious calls, deep-dive via RAG:
```
mcp__rag__search(query="Tool Call N: [tool name]", collection="Subagents")
```

- **Total calls:** X
- **Useful calls:** Y
- **Efficiency:** Y/X

### 4.4 Format Compliance (20%)

- Did agent follow requested output format?
- Missing sections?
- Extra unrequested sections?

### 4.5 Scope Control (15%)

- Did agent deliver what was asked, nothing more?
- Scope creep present?
- Stop criteria respected?

### 4.6 Path Hygiene (5%)

- Local paths in output? (`/Users/...`)
- Relative paths used correctly?

### 4.7 Model-Specific Issues

Based on the model used (from Phase 3):

**Haiku:**
- [ ] Format drift (own format instead of requested)
- [ ] Scope creep (delivered more than asked)
- [ ] Path hallucinations
- [ ] Stop criteria ignored

**Sonnet/Opus:**
- [ ] Over-engineering
- [ ] Unnecessary verbosity

### 4.8 Dispatch Quality

Evaluate the **Dispatch Context** section from the MD file (NOT indexed — read directly from MD).

Read the dispatch context from the MD file:
```bash
head -300 "$OUTPUT_MD" | grep -A 1000 "# Dispatch Context" | grep -B 1000 "# Task Prompt" | head -200
```

Evaluate three aspects:

| Aspect | Rating | Comment |
|--------|--------|---------|
| Task Clarity | OK/Weak/Poor | Was the task prompt precise enough for the sub to succeed? |
| Context Sufficiency | OK/Weak/Poor | Did the sub receive all necessary context (file paths, constraints, scope)? |
| Response Processing | OK/Weak/Poor | Did the main agent meaningfully use the sub's response? |

**Guiding questions:**
- Could the task prompt have been worded more precisely?
- Did the main provide relevant file paths, constraints, or scope limits?
- Did the main blindly copy the sub's response or critically evaluate it?
- Were there obvious context gaps that caused the sub to underperform?

**Root cause link:** If the sub scored low on Task Fulfillment (4.2), check whether the dispatch quality was the actual root cause (bad task = bad result).

### 4.9 Overall Score

| KPI | Weight | Score | Weighted |
|-----|--------|-------|----------|
| Task Fulfillment | 35% | X% | |
| Tool Efficiency | 25% | X% | |
| Format Compliance | 20% | X% | |
| Scope Control | 15% | X% | |
| Path Hygiene | 5% | X% | |
| **Total** | | | **X%** |

**Target:** >85%

---

## Phase 5: Automation File Proposal

### Root Cause Analysis

| Problem | Symptom | Root Cause | Automation File |
|---------|---------|------------|-----------------|
| [Name] | [What happens] | [Why] | [Which file] |

### Concrete Proposals

For EACH identified problem, provide a concrete proposal:

**Format:**

```
### Proposal N: [Title]

**File:** [Full path to automation file]
**Location:** [Line range or section name]
**KPI Impact:** [Which KPI this addresses, current score → expected score]

**WHY:** [Root cause explanation — what went wrong and why this file is responsible]

**Current:**
[Exact current text at that location]

**Proposed:**
[Exact replacement text]

**Expected Impact:** [Concrete improvement description]
```

**CRITICAL:**
- Every proposal MUST have a WHY — no changes without root cause justification
- Proposals are SUGGESTIONS — do NOT edit any files
- Be specific: exact file, exact location, exact text

**STOP** - Present all proposals to user. Ask: "Which proposals should be implemented?"

---

## Phase 6: Cleanup

### Step 1: Delete from RAG Collection

```bash
cd ${CLAUDE_PLUGIN_ROOT} && \
./venv/bin/python workflow.py delete --collection Subagents --document ${AGENT_ID}.md
```

### Step 2: Remove Temp Files

```bash
rm ${CLAUDE_PLUGIN_ROOT}/data/documents/Subagents/${AGENT_ID}.md
rm ${CLAUDE_PLUGIN_ROOT}/data/documents/Subagents/${AGENT_ID}.json
```

### Step 3: Verify

```
mcp__rag__list_documents(collection="Subagents")
```

Collection should be empty (or not contain the evaluated agent).
