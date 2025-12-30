---
name: iterative-dev
description: (project)
---

# Iterative Development Skill

## Overview

This skill extends native Claude Code Plan Mode with:
- Phase indicators
- Iterative cycle structure
- Explicit file vs chat separation

Follow all native Plan Mode rules.

## Facts Over Assumptions (CORE PRINCIPLE)

**ALWAYS verify first. NEVER assume.**

Before ANY action, ask yourself:
- Can I verify this? → VERIFY IT
- Is this 100% self-evident logic? → Only then proceed
- Am I guessing? → STOP. Read. Ask.

**The Name Test:**
> Imagine your name is printed under every statement you make.
> Would you want your name under "ASSUMPTION" or "FACT"?

**Verification Hierarchy:**
1. READ the file/code/docs
2. ASK the user
3. RUN a command to check
4. ONLY THEN: proceed

**Assumptions are ONLY acceptable when:**
- The matter is purely logical (2+2=4)
- There is literally no way to verify
- AND you explicitly document it as "ASSUMPTION: ..."

**Red Flags (you're assuming):**
- "I think..." → STOP, verify
- "It should be..." → STOP, read
- "Probably..." → STOP, ask
- Using tool without checking valid params/types first

**This applies to EVERYTHING:**
- Tool parameters (check --help first)
- File paths (ls before using)
- API responses (read schema/docs)
- User intent (ask before implementing)

## Task Management Hierarchy

- **Beads** (`.beads/`) - Cross-session (weeks/months)
- **Plan-File** (`.claude/plans/`) - Within a session (hours)
- **TodoWrite** - Within an iteration (minutes)

## Automation Stellschrauben (Hierarchy)

Six layers for Claude Code automation, from project-wide to atomic:

| Layer | Scope | Location | When to Modify |
|-------|-------|----------|----------------|
| **CLAUDE.md** | Project-wide | `/project/CLAUDE.md` | Universal rules, philosophy, communication protocols |
| **Skills** | Session | `.claude/skills/*/SKILL.md` | Workflow patterns, phases, evaluation criteria |
| **Commands** | Workflow | `.claude/commands/*.md` | Repeatable procedures with steps/stops |
| **Agents** | Task | `.claude/agents/*.md` | Subagent behavior, output format, task scope |
| **Hooks** | Atomic | `~/.claude/scripts/` | Event interception, blocking, output silencing |
| **Scripts** | Pipeline | Project-specific (e.g., `postprocess.py`) | Automation logic, data transformations |

### Relationships

```
CLAUDE.md ──── influences ────> Everything

Skills ──┬── provide context for ──> Commands (optional)
         └── spawn ────────────────> Agents

Commands ──── spawn ───> Agents

Hooks ──── fire on ───> User Prompts + Tool Calls (all layers)

Scripts ──── called by ───> Commands, Agents, direct execution
```

### Skill + Command Interaction

When a **slash command** is called within a skill phase:

1. Skill phase is **FROZEN**
2. User exits Plan Mode
3. Claude executes command until its stoppers
4. After command completes → skill phase resumes

Commands are self-contained workflows. Skills provide context but don't interfere with command execution.

### Improvement Flow

For EVERY improvement in RECAP:

1. Ask: **"Is this a one-time fix or a pattern?"**
2. If PATTERN → Identify the correct Stellschraube:
   - Applies everywhere? → CLAUDE.md
   - Applies to this skill/workflow? → SKILL.md
   - Is a repeatable workflow? → Command
   - Affects subagent behavior? → Agent
   - Should intercept events? → Hook
   - Is automation logic? → Script

3. **NEVER** let recurring issues stay as "process improvements" without Stellschraube integration

### When Creating Commands

Ask user for reference command. Don't invent patterns.

## CRITICAL CYCLE

```
PLAN (Plan Mode) -> IMPLEMENT -> RECAP -> IMPROVE -> CLOSING -> PLAN (new cycle)
```

EVERY RESPONSE STARTS WITH A PHASE INDICATOR:
- `📋 PLAN` - Planning phase (Plan Mode active)
- `🔨 IMPLEMENT` - Implementation phase
- `🔍 RECAP` - Report phase (Plan Mode active - read-only enforced)
- `🛠️ IMPROVE` - Improvements phase
- `✅ CLOSING` - Cycle completion

**Plan Mode Usage:**
- PLAN: Native Plan Mode for implementation planning
- RECAP: Plan Mode for read-only protection (prevents accidental edits)

**Phase Detection:** System message contains "Plan mode is active" → Check context to determine if PLAN or RECAP.

---

## Planning Phase (PLAN)

### Scoping (BEFORE Exploration)

BEFORE you explore, clarify with the user:

**1. SCOPE - What is the end goal?**
→ "What should the output be?"
→ File? Script? Documentation? Analysis?

**2. SOURCES - Which files/folders are relevant?**
→ "Which folders should I look at?"
→ "Is there a reference script?"
→ User knows the structure better than you

**3. CONNECTIONS - How do the sources relate?**
→ "How does X use data from Y?"
→ Only when connections are clear: read DOCS.md

**THEN:** Explore with direction (DOCS.md → relevant scripts → structures)

### Exploration

**Documentation First (MANDATORY):**

BEFORE any action in a directory (running scripts, editing files, exploring code):
1. STOP
2. READ the DOCS.md in that directory
3. ONLY THEN proceed

This is NON-NEGOTIABLE. Skipping DOCS.md leads to: wrong paths, wrong arguments, wrong understanding.

**Path Verification (MANDATORY):**

BEFORE executing scripts with relative paths:
1. Verify paths with `ls` command
2. NEVER assume paths are correct just because script exists
3. One wrong path = entire workflow fails silently

**ASK THE FUCKING USER**
- the user knows best, ask him for reference scripts, 
	- REFERENCE SCRIPTS OR SOURCE CODE IS A GAME CHANGER, MAKES LIFE MUCH EASIER
- ask him for things which are critical to understand in order to be able to make a Plan file
	- USER HAS A BROAD KNOWLEDGE, TAKE ADVANTAGE OF IT

### Communication

| Channel | Purpose |
|---------|---------|
| Chat | Brainstorming, asking questions |
| Plan file | Key points and implementation steps |

**Proactivity (CRITICAL):**
- On skill start: Ask context questions IMMEDIATELY, don't wait
- Clarify SCOPE, SOURCES, CONNECTIONS first
- THEN explore with clear direction

**Questions:**
- One question at a time, based on previous answer, prefer multiple choice, 'askuserquestion' tool
- Questions building up on each other, one leads to another

**Plan-File:**
- Use system-provided plan file path from Plan Mode message
- ALWAYS use Write/Edit tool to update plan file
- NEVER write plan content directly in chat

### Plan File Management

**Core Principle:** Build the plan ITERATIVELY.

- **CRITICAL:**
- After each chat exchange: UPDATE the plan file
- Never write the complete plan at once
- Plan grows organically through conversation
- Only call ExitPlanMode when plan reflects current understanding

### Execution During Planning

If the planning session requires module execution to refine the plan:
1. Call ExitPlanMode
2. Execute only what is needed to refine the plan
3. Ask user to manually return to plan mode

### Before ExitPlanMode

- Plan file MUST reflect current implementation approach
- NEVER call ExitPlanMode with stale plan

---

## Implementation Phase (IMPLEMENT)

- execute whats stated in the PLAN file

### After IMPLEMENTATION

**Principle:** One phase per response. Never combine IMPLEMENT and RECAP in same response.

1. Verify all plan items were executed
2. **If open points remain:** Inform user: "Open items: [list]"
3. Ask: "Continue implementing or proceed to RECAP?"

User confirms → next response starts with 🔍 RECAP

### Ad-hoc Window

After completing plan edits, BEFORE transition to RECAP:

1. Claude: "Plan edits completed. Proceed to RECAP?"
2. User can request ad-hoc edits
3. Claude executes ad-hoc edits
4. Back to step 1 until user says "eval"

**CRITICAL:** This window is the ONLY place for ad-hoc edits.

---

## Recap Phase (RECAP)

### Phase Entry

1. Ask user: "Activate Plan Mode for RECAP (`/plan`)"
2. Wait for Plan Mode system message
3. Proceed with evaluation report (read-only enforced by Plan Mode)

### Plan File Handling

**CRITICAL:** Report OVERWRITES plan file completely.

- **Executed tasks:** Only mentioned in Execution summary
- **Open items:** Listed in "## Open Items" section → handled in CLOSING phase (Bead or discard)
- **No "ORIGINAL PLAN" section** - plan is consumed by execution

### Report

Claude writes a report that OVERWRITES the plan file:

#### 1. Execution

- What matched the Plan File, what deviated from the Plan File

#### 2. Process Reflection

Explicitly analyze the planning phase across two dimensions:

##### 2.1 Efficiency

###### Questions During Planning
- Were my questions focused or scattered?
- Did we iterate too much? Could we have reached the finished plan faster?
- Did I correctly understand the user's answers?
- Did the user give insightful answers?

###### Red Flags
- More than 3 back-and-forth exchanges before stable plan
- User had to correct my assumptions multiple times
- I proposed solutions before understanding the problem
- Execution Path Errors (Most IMPLEMENT failures trace back to skipped verification in PLAN)
- User did not explicitly state what he wants, gave bad directions
- User did not understand you

###### References
- Did I explicitly ask for references early enough?
- Were the references helpful or did they lead me astray?
  - Should the references have been more granular or broader?

##### 2.2 Assumptions/Hallucinations

###### Questions
- Did I make assumptions that needed correction?
- Was the user's intent clear from the start?
- Did I verify assumptions or just proceed?

###### Categories
- **Structural:** Directory layout, file locations, naming conventions
- **Semantic:** What columns mean, what functions do, data flow
- **Behavioral:** Expected output format, error handling, edge cases

###### Rule
Every assumption should be either:
1. Verified by reading code/docs
2. Explicitly confirmed with user
3. Documented as "ASSUMPTION: ..." in plan file

##### 2.3 Algorithm Investigation

When investigating WHY something behaves a certain way (selection logic, thresholds, metrics):

1. **ASK FOR SOURCE CODE IMMEDIATELY**
   - "Where is [metric] calculated?"
   - "Which file contains the selection logic?"

2. **NEVER assume metric definitions**
   - avg_mre, error_score, delta - these are algorithm-specific
   - Read the calculation, don't infer from name

3. **Trace the data flow**
   - What data goes in? (Training_Test? Test?)
   - When is it calculated? (Once? Per iteration?)
   - What triggers recalculation?

**Red Flag:** Making hypothesis about algorithm without reading source = hallucination risk

#### 3. Hooks Evaluation

Evaluate current hooks for improvements:

**Questions:**
- Did a hook block something it shouldn't have?
- Did a hook allow something it should have blocked?
- Is output silencing helping or hiding problems?
- Should a recurring command pattern become a hook rule?

**Improvement Candidates:**
- Commands that failed due to missing hook rules
- Verbose output that polluted context
- Security patterns that should be blocked

**Reference:** `~/.claude/scripts/README.md`

#### 4. Agent Evaluation

Evaluate subagent usage during the cycle (if agents were used).

##### Output Quality

| Aspect | Rating | Criteria |
|--------|--------|----------|
| Format | ✅/⚠️/❌ | Did agent follow requested output format? |
| Relevance | ✅/⚠️/❌ | Were findings relevant to the task? |
| Completeness | ✅/⚠️/❌ | Did agent find all critical files/info? |
| Actionability | ✅/⚠️/❌ | Could I act on the output without additional research? |

##### What Helped
- List concrete benefits from agent usage

##### What Could Be Better
- Specific improvements for agent prompts or output

##### Missed Agent Usage

Identify situations where agent should have been used but wasn't:

| Situation | What I Did | What I Should Have Done |
|-----------|-----------|------------------------|
| ... | Manual search | Use agent for exploration |

**When to Use Agent:**
- Exploration over >3 files
- Unknown directory structure
- Pipeline tracing (input → output)
- When hook requests it

**When NOT to Use Agent (do it yourself):**
- Direct reads of known paths
- Verification after agent output
- Single targeted grep/glob

#### 5. Beads Evaluation

Run `bd list` to check open beads, then evaluate:

##### 5.1 New Beads

Discovered work that should be tracked cross-session?
- List candidates with proposed title/type

##### 5.2 Update Existing Beads

For each open bead worked on this session:
- Progress made?
- New blockers/dependencies?
- Comments to add?

##### 5.3 Close Completed Beads

For each bead completed this session:
- Mark for closing with reason

**Format:** `<id>: <reason>`

Example: `Thesis_Final-e0m: Fixed MIN_ERROR_THRESHOLD by adjusting selection logic in 10_Pattern_Selection.py`

#### 6. Improvements

Improvements are based on the execution and process reflection.

##### 6.1 Content Improvements (Code/Docs)

- **Critical:** Must fix (breaks functionality, wrong behavior)
- **Important:** Should fix (code quality, maintainability)
- **Optional:** Nice to have (style, minor optimizations)

##### 6.2 Process Improvements

Same 3 categories, but graded by OUTCOME:

- **Critical:** Process issues that WOULD HAVE caused critical code issues
  - Example: Skipping path verification → wrong file edited
  - Example: Not reading DOCS.md → wrong arguments used

- **Important:** Process issues that caused detours but correct outcome
  - Context pollution (too much irrelevant output)
  - Off-the-rails analysis (wrong hypothesis, user had to correct)
  - Circles (repeated attempts at same thing)
  - Example: Wrong assumption about avg_mre → user corrected → correct result with delay

- **Optional:** Minor process inefficiencies
  - Could have asked better questions
  - Could have parallelized better

**Key insight:** The OUTCOME determines severity. Wrong process + correct result = Important (not Critical).

##### 6.3 DOCS.md Check (MANDATORY)

**ALWAYS explicitly answer:**
- Does DOCS.md need updating? YES/NO
- If YES: What sections? (new scripts, changed parameters, new outputs)

Clean docs are CRITICAL. Every new script, changed behavior, or new parameter MUST be reflected.

#### 7. Stellschrauben Assessment

For EVERY improvement from Section 6, explicitly map to a Stellschraube:

| Improvement | Stellschraube | Action |
|-------------|---------------|--------|
| [description] | CLAUDE.md / SKILL.md / Command / Agent / Hook / Script | [specific change] |

**Rules:**
- One-time fix? → Just implement, no Stellschraube
- Pattern/recurring? → MUST go into appropriate Stellschraube
- Unsure which? → Ask user

**Categories:**
- **CLAUDE.md**: Universal rules, philosophy, communication protocols
- **SKILL.md**: Workflow patterns, phase behaviors, evaluation criteria
- **Command**: Repeatable procedures with defined steps/stops
- **Agent**: Subagent behavior, output format, task scope
- **Hook**: Event interception, blocking, output silencing
- **Script**: Automation logic, data transformations

#### 8. Open Items

List any tasks from the original plan that were NOT executed.
- These will be handled in CLOSING phase (create Bead or discard)

### Collecting Improvements

After report:
1. Ask: "Any remarks?"
2. User gives remark → Add to Improvements section
3. Ask: "More remarks?"
4. Repeat until user says "done" or "improve"

### Phase Exit

1. Ensure all improvements are written to plan file
2. Call ExitPlanMode
3. Next response starts with 🛠️ IMPROVE

---

## Improve Phase (IMPROVE)

**Purpose:** Execute improvements from plan file (like IMPLEMENT, but for improvements).

### Content Improvements: Beads vs Direct Edit

**CRITICAL:** IMPROVE has no validation/test phase after it.

| Improvement Type | Action |
|------------------|--------|
| Code changes (*.py, *.yml, etc.) | → Create Bead (next cycle validates) |
| Documentation (README, DOCS, CLAUDE.md) | → Direct edit in IMPROVE |
| SKILL.md updates | → Direct edit in IMPROVE |

**Rationale:** Code changes need testing. IMPROVE → CLOSING has no test step. So code changes become Beads and get their own PLAN → IMPLEMENT → RECAP cycle with proper validation.

### Workflow

1. Read plan file "## Improvements" section
2. For each improvement:
   - **Code change?** → `bd create --title "..." --type=...`
   - **Docs change?** → Execute directly (Edit, Write)
3. Handle other Beads (from RECAP evaluation):
   - Create new beads: `bd create --title "..." --type=...`
   - Update beads: `bd comment <id> "..."`
   - Close beads: `bd close <id> --reason="..."`
4. Ask: "Proceed to CLOSING?"

User confirms → next response starts with ✅ CLOSING

---

## Closing Phase (CLOSING)

Only enter when user confirms (e.g., "proceed", "close", "done").

1. Update DOCS.md (if needed)
2. Handle open items (non-beads):
   - For each open item, ASK: "Should [Item X] go to Beads? (cross-session)"
   - User confirms → handled in next cycle's IMPROVE
   - User declines → Keep in plan file for next iteration
   - If no open items remain: clear plan file (overwrite with single space)
3. Finalize:
   - `bd sync`
   - `git add . && git commit`
   - `git push`
4. Ask: "New cycle or done for now?"
