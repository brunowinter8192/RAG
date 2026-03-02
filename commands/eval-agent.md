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

```python
import sys, json
from pathlib import Path
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}')
from src.rag.chunker import chunk_workflow

chunks = chunk_workflow("$OUTPUT_MD", chunk_size=1500, overlap=200)

output = {
    "document": "$AGENT_ID.md",
    "chunks": [
        {"index": i, "content": c['content']}
        for i, c in enumerate(chunks)
    ]
}

json_path = Path("$OUTPUT_MD").with_suffix('.json')
with open(json_path, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Created {len(chunks)} chunks -> {json_path}")
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

## Phase 4: Evaluate & Propose

### Step 1: Read Session

Read dispatch context, task prompt, tool call summary, and final response:

```
mcp__rag__read_document(collection="Subagents", document="${AGENT_ID}.md", start_chunk=0, num_chunks=5)
```

This returns:
- **Dispatch Context** (Chunk 0-1): Main agent's reasoning before dispatch + how it processed the result
- **Task prompt** (Chunk ~2): What was the agent supposed to do?
- **Tool Call Summary** (Chunk ~3): All tool calls in sequence with output sizes
- **Final response** (Chunk ~4): What did the agent deliver?

Also read dispatch context from MD file directly:
```bash
head -300 "$OUTPUT_MD" | grep -A 1000 "# Dispatch Context" | grep -B 1000 "# Task Prompt" | head -200
```

For suspicious tool calls, deep-dive via RAG:
```
mcp__rag__search(query="Tool Call N: [tool name]", collection="Subagents")
```

### Step 2: Analyze

Look for issues across these dimensions (checklist, not scoring):
- **Task fulfillment:** Requirements met? Gaps?
- **Tool efficiency:** Redundant calls? Wasted reads? Oversized outputs?
- **Format compliance:** Requested output format followed?
- **Scope control:** Delivered what was asked, nothing more?
- **Path hygiene:** Local paths in output?
- **Dispatch quality:** Was the task prompt precise enough? Did the main process the response well?

### Step 3: Write Proposals

For EACH issue found, write one proposal:

```
### Proposal N: [Title]

**Observation:** [What happened — concrete, factual]

**Proposal:**
- **File:** [Full path to automation file]
- **Location:** [Section name or line range]
- **Current:** [Exact current text]
- **Proposed:** [Exact replacement text]

**Reasoning:** [Why this file caused the issue, why this fix addresses it]
```

**CRITICAL:**
- Proposals are SUGGESTIONS — do NOT edit any files
- Be specific: exact file, exact location, exact text
- Every proposal needs all 3 parts (Observation, Proposal, Reasoning)

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
