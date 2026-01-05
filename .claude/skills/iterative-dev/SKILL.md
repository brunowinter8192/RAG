---
name: iterative-dev
description: (project)
---

# Iterative Development Skill

## Task Management Hierarchy

- **Beads** (`.beads/`) - Cross-session (weeks/months)
- **Plan-File** (`.claude/plans/`) - Within a session (hours)
- **TodoWrite** - Within an iteration (minutes)

### Beads CLI Gotchas

**`bd edit --title`** opens vim (interactive) → **FAILS in Claude Code**

**Workarounds:**
- Rename scope? → `bd comment <id> "New scope: ..."`
- Merge beads? → `bd close <id> --reason="Merged into <other-id>"`
- Create with full info: `bd create --title "..." --type=... --description="..."`

**Commands that WORK:**
- `bd list` / `bd show <id>`
- `bd create --title "..." --type=...`
- `bd comment <id> "..."`
- `bd close <id> --reason="..."`
- `bd sync`

### Bead Content Requirements

**CRITICAL:** Beads are cross-session. A new session has NO context.

**Rule:** Every bead MUST contain enough information to understand it WITHOUT the original session context.

**On Create:**
- `--description` is MANDATORY for non-trivial beads
- Description answers: What? Why? Where? (files/modules affected)
- Bad: `--title "Fix bug"` (useless in new session)
- Good: `--title "Fix NaN in search scores" --description="search_workflow returns NaN when query has no matches. Affects src/rag/retriever.py"`

**On Update:**
- `bd comment` for progress, blockers, decisions
- Each comment should be self-contained (not "fixed it" but "fixed by adding null check in line 42")

**On Close:**
- `--reason` must explain WHAT was done, not just "done"
- Bad: `--reason="Fixed"`
- Good: `--reason="Added null check in retriever.py:42, now returns empty list instead of NaN"`

**Test:** Can someone in a new session understand this bead without asking?

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

### Beads Check (BEFORE Exploration)

**MANDATORY:** Run `bd list` BEFORE launching any exploration agents.

Beads provide cross-session context. Agent exploration without bead context = wasted effort.

### Scoping (BEFORE Exploration)

BEFORE you explore, clarify with the user:

**1. SCOPE - What is the end goal?**
→ "What should the output be?"
→ File? Script? Documentation? Analysis?
→ **If Documentation:** "Who is the target reader?"
  - **Default assumption:** AI (you) is the primary reader
  - Docs should be perfect for AI consumption, but human-readable when needed
  - Optimize for: clarity, structure, completeness (AI needs full context)

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

**ASK THE FUCKING USER**
- the user knows best, ask him for reference scripts,
	- REFERENCE SCRIPTS OR SOURCE CODE IS A GAME CHANGER, MAKES LIFE MUCH EASIER
- ask him for things which are critical to understand in order to be able to make a Plan file
	- USER HAS A BROAD KNOWLEDGE, TAKE ADVANTAGE OF IT
- **External Dependencies/Versions:** ASK USER, don't self-verify
	- Docker images, tool versions, library versions
	- User knows what was ACTUALLY USED vs what's CURRENTLY AVAILABLE
	- Reproducibility > Recency (especially for research/thesis)

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
- **ALWAYS ask "Any remarks?" and wait for user signal** ("done", "continue", "implement")
  - Saves tokens (no rejected ExitPlanMode calls)
  - User controls transition timing

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

**CRITICAL:** Every improvement MUST reference a Stellschraube from project CLAUDE.md.
Improvements without concrete target path are not actionable → reject.

→ **See project CLAUDE.md for available Stellschrauben and paths.**

##### 6.1 Content Improvements (Code/Docs)

Prioritization:
- **Critical:** Must fix (breaks functionality, wrong behavior)
- **Important:** Should fix (code quality, maintainability)
- **Optional:** Nice to have (style, minor optimizations)

**Handling in IMPROVE Phase:**
- Code (*.py, *.yml, etc.) → **Bead** (needs own PLAN→IMPLEMENT→RECAP cycle)
- Docs/README/Stellschrauben → **Direct Edit** in IMPROVE

##### 6.2 Process Improvements

Prioritization (by OUTCOME):
- **Critical:** Process errors that WOULD HAVE caused critical code issues
- **Important:** Process errors that caused detours but correct outcome
- **Optional:** Minor process inefficiencies

**Handling in IMPROVE Phase:**
- Stellschrauben (Skills, Commands, Agents, Hooks) → **Direct Edit** in IMPROVE
- Docs/README → **Direct Edit** in IMPROVE
- Code → **Bead**

**Key insight:** OUTCOME determines severity. Wrong process + correct result = Important (not Critical).

##### 6.3 DOCS.md Check (MANDATORY)

**ALWAYS explicitly answer:**
- Does DOCS.md need updating? YES/NO
- If YES: What sections? (new scripts, changed parameters, new outputs)

Clean docs are CRITICAL. Every new script, changed behavior, or new parameter MUST be reflected.

#### 7. Open Items

List any tasks from the original plan that were NOT executed.
- These will be handled in CLOSING phase (create Bead or discard)

### Collecting Improvements

After report:
1. Ask: "Any remarks?"
2. User gives remark → **Analyze for system improvement**
3. Ask: "More remarks?"
4. Repeat until user says "done" or "improve"

**CRITICAL: Remarks → Analyze → Propose Improvement + Location**

When user gives ANY remark:
1. **Analyze:** What went wrong? What could be better?
2. **Propose:** Concrete improvement
3. **Locate:** WHERE the improvement would happen (Stellschraube from CLAUDE.md)

**Output Format:**
```
Remark: [User's remark]
Analysis: [What went wrong]
Improvement: [Concrete change]
Location: [Stellschraube + file path from CLAUDE.md]
```

**The Goal:** Every remark → concrete improvement proposal with exact location.

### Phase Exit

1. Ensure all improvements are written to plan file
2. Call ExitPlanMode
3. Next response starts with 🛠️ IMPROVE

---

## Improve Phase (IMPROVE)

**Purpose:** Execute improvements from plan file.

**CRITICAL:** IMPROVE has no validation after it. Therefore:
- Code → Bead (own cycle with validation)
- Everything else → Direct Edit

### Workflow

1. Read plan file "## Improvements" section
2. For each improvement (see 6.1/6.2 Handling):
   - **Code?** → `bd create --title "..." --type=...`
   - **Docs/README/Stellschrauben?** → Direct Edit (Edit, Write)
3. Handle Beads (from RECAP Section 5):
   - Create: `bd create --title "..." --type=...`
   - Update: `bd comment <id> "..."`
   - Close: `bd close <id> --reason="..."`
4. Ask: "Proceed to CLOSING?"

User confirms → next response starts with ✅ CLOSING

---

## Closing Phase (CLOSING)

Only enter when user confirms (e.g., "proceed", "close", "done").

1. `bd sync`
2. `git add . && git commit`
3. `git push`
4. Ask: "New cycle or done for now?"
