# Evaluation: git-committer — agent-a5cd1313fdd2ad77e

**Session:** 82d1d6ac-1b8b-4180-9db4-dab44a7dfe5b (RAG project, 2026-03-10 23:29-23:30)
**Agent:** iterative-dev:git-committer (Haiku)
**Task:** Commit changes in /Users/brunowinter2000/Documents/ai/Meta/ClaudeCode/MCP/RAG
**Result:** FAILED — commit blocked by pre-commit hook, 0 commits made

---

## Scorecard

| KPI | Score | Begründung |
|-----|-------|-----------|
| Task Fulfillment | 0% | Kein Commit. Blocker korrekt erkannt, aber nicht lösbar. |
| Tool Efficiency | 45% | 20 Calls für 0 Commits. 5 Investigation-Calls vor erstem Commit-Versuch. Read-Tool verwendet (verboten). |
| Format Compliance | 20% | Output-Format verletzt: Prose + Optionsmenü statt strukturiertem Blocksatz. Read-Tool verwendet (FORBIDDEN). |
| Scope Control | 75% | Agent blieb weitgehend on-task. Leichte Investigation-Ausweitung nach dem Blocker. |
| Path Hygiene | 100% | Keine lokalen Pfade im Output. |
| **Gesamt** | **45%** | |

**Ziel:** >85%

---

## Was gut lief

- Pre-commit Hook korrekt als Blocker identifiziert
- `bd export` nach `bd sync --flush-only` korrekt versucht (entspricht FORBIDDEN-Regel "if hook mentions bd: run bd export once")
- HEREDOC-Format für Commit-Message korrekt
- Untracked `dev/llama_server/` korrekt erkannt und staged
- Import-Cross-Check (Call #3 diff) korrekt durchgeführt

---

## Was schiefging

### Problem 1: Read-Tool verwendet (FORBIDDEN-Verletzung)

**Call #18:** `Read: file_path=.git/hooks/pre-commit`

Das Agent-Definition FORBIDDEN-Section sagt explizit: **"Using the `Read` tool — never read full file contents."**

Der Agent hat stattdessen die Bash-Alternative (`cat .git/hooks/pre-commit`) ignoriert und direkt das Read-Tool aufgerufen.

Der Schaden: Minimalregelverletzung. Die Information war korrekt. Aber die Regel existiert aus gutem Grund (Sicherheit, klar definiertes Tool-Scope).

---

### Problem 2: Output-Format verletzt — Prose + Optionsmenü

Der Agent gab zurück:
```
No other untracked files. The hook issue is a blocker due to the outdated bd command. Since
the hook itself is broken (the `bd` command doesn't support `sync --flush-only`), I need to
report this issue: [...]

Would you like me to:
1. Fix the hook in the repo to use `bd export` instead
2. Disable the hook temporarily to allow the commit
3. Investigate whether the hook is necessary for this repo
```

Die FORBIDDEN-Section sagt klar: **"Prose, summaries, explanations, or suggestions"** sind verboten.

Es gibt kein definiertes Output-Format für `COMMIT_BLOCKED`. Das Agent-Format definiert nur: `REPO`, `FILES`, `COMMIT`, `PUSHED`, `PUSH_FAILED`. Ein Blocker-Szenario fehlt vollständig.

**Folge:** Statt einem sauberen strukturierten Block lieferte der Agent ein interaktives Optionsmenü — das exakte Gegenteil des definierten "no prose, no suggestions" Prinzips.

---

### Problem 3: Exzessive Investigation-Calls (5 statt 3)

Calls #1-5:
1. `git status` (352 chars)
2. `git diff --stat` (105 chars)
3. `git diff src/rag/reranker.py src/rag/retriever.py` (304 chars)
4. `git diff --cached .beads/backup/backup_state.json` (391 chars)
5. `git diff src/rag/retriever.py` (354 chars) — **Call #5 ist Duplikat von Call #3 (selbe Datei)**

Call #5 ist redundant. EXECUTION ORDER sagt: status → diff → diff --cached → stage. Drei Calls, dann weiter. Der Agent hat `retriever.py` zweimal gedifft.

---

### Problem 4: Commit-Message ungenau

Agent-Commit-Message (Call #13):
> "fix: tune reranker llama-server batch parameters — Increased RERANK_CANDIDATES from 10 to 50 to match HYBRID_CANDIDATES"

Tatsächlicher Commit-Content (aus git log nach manueller Korrektur durch Main Agent):
> "fix: reranker 500 error — add -ub/-b 4096 batch size flags"

Der Agent sah nur die Diffs von `reranker.py` und `retriever.py` (304+354 chars), die wahrscheinlich nur Teile der Änderungen enthielten. Die `dev/llama_server/` Dateien (neue Dateien, kein diff) wurden erst in Call #11 gestaged. Das führte zu einer unvollständigen Informationsbasis für die Commit-Message.

**Root cause:** Der Agent hat die Commit-Message generiert bevor er wusste, welche Dateien insgesamt committed werden (dev/llama_server/ wurden erst später discovered).

---

## Dispatch-Qualität

| Aspekt | Rating | Kommentar |
|--------|--------|-----------|
| Task Clarity | OK | Klarer Repo-Pfad, minimal aber ausreichend |
| Context Sufficiency | Weak | Kein Hinweis auf ausstehende Hook-Probleme. Main Agent wusste vom `bd sync` Problem (Post-Dispatch: "Pre-commit Hook blockiert wegen veraltetem bd sync"). Diese Information wäre als Dispatch-Kontext wertvoll gewesen. |
| Response Processing | OK | Main Agent hat das Problem korrekt verstanden und die Hook selbst gefixt |

**Root cause link:** Der Blocker (bd sync → bd export) war dem Main Agent bekannt, wurde aber nicht im Dispatch mitgegeben. Hätte der Dispatch `"Note: pre-commit hook may use 'bd sync --flush-only' — if it fails, run 'bd export' once and retry"` enthalten, hätte der Agent direkt den richtigen bd-Befehl versucht.

---

## Proposals

### Proposal 1: COMMIT_BLOCKED Output-Format definieren

**File:** `/Users/brunowinter2000/Documents/ai/Meta/blank/agents/git-committer.md`
**Location:** Section "CRITICAL: Output Format"

**WHY:** Das Output-Format definiert Formate für SKIP, PUSH_FAILED etc., aber keins für COMMIT_BLOCKED. Haiku füllt diese Lücke mit Prose und Optionsmenü (FORBIDDEN). Eine explizite Format-Definition verhindert das.

**Current:**
```
If push failed:

```
REPO: <repo-name> (branch)
COMMIT: <hash> <message>
PUSH_FAILED: <error message>
```
```

**Proposed:**
```
If push failed:

```
REPO: <repo-name> (branch)
COMMIT: <hash> <message>
PUSH_FAILED: <error message>
```

If commit blocked by pre-commit hook:

```
REPO: <repo-name> (branch)
COMMIT_BLOCKED: <hook name> — <error message>
```

**FORBIDDEN:** Options, suggestions, or "Would you like me to..." — report the error and STOP.
```

**Expected Impact:** Agent liefert strukturierten COMMIT_BLOCKED-Block statt Prose + Optionsmenü.

---

### Proposal 2: Read-Tool FORBIDDEN — Bash-Alternative explizit nennen

**File:** `/Users/brunowinter2000/Documents/ai/Meta/blank/agents/git-committer.md`
**Location:** Section "FORBIDDEN"

**WHY:** Das FORBIDDEN "Using the `Read` tool" ist klar formuliert, aber ohne Alternative. Wenn der Agent den Hook-Inhalt braucht (z.B. um zu verstehen warum `bd` fehlschlägt), greift er auf Read zurück weil die Bash-Alternative nicht explizit erwähnt wird.

**Current:**
```
- **Using the `Read` tool** — never read full file contents. `git diff` output is the only allowed way to understand changes.
```

**Proposed:**
```
- **Using the `Read` tool** — never read full file contents. `git diff` is the only allowed way to understand code changes. Exception: if you need to read a config file (e.g., a git hook), use `Bash: cat <path>` instead of the Read tool.
```

**Expected Impact:** Agent liest Hooks via `cat` (Bash) statt Read-Tool. Kein FORBIDDEN-Verstoß.

---

### Proposal 3: Commit-Message-Timing — Stage first, then generate

**File:** `/Users/brunowinter2000/Documents/ai/Meta/blank/agents/git-committer.md`
**Location:** Section "CRITICAL: Execution Order", Step 7

**WHY:** Der Agent generierte die Commit-Message aus dem Diff von reranker.py+retriever.py (Steps 3-5), bevor er die untracked dev/llama_server/ Dateien entdeckt hatte (Step 8-11). Die Message war daher unvollständig.

**Current:**
```
7. Generate commit message from the diff (see Commit Message Rules)
8. Commit with HEREDOC format (see below)
```

**Proposed:**
```
7. Generate commit message from ALL staged files:
   - Run `git diff --cached --stat` after step 5b (staging complete) — this shows EVERYTHING staged
   - Base the commit message on the full staged diff, not on pre-staging diffs
   - For new untracked files: use `git show --stat HEAD` equivalent via `git diff --cached --name-only`
8. Commit with HEREDOC format (see below)
```

**Expected Impact:** Commit-Message basiert auf dem vollständigen staged state, nicht auf den initialen Investigation-Diffs. Verhindert inaccurate Messages.

---

### Proposal 4: Hook-Context im Dispatch (Dispatcher-SKILL)

**File:** Nicht anwendbar direkt — dies ist eine Dispatcher-seitige Verbesserung.

**WHY:** Der Main Agent wusste vom `bd sync` Problem (erkennbar aus Post-Dispatch: "Pre-commit Hook blockiert wegen veraltetem bd sync"). Diese Information wurde nicht im Dispatch-Prompt mitgegeben. Hätte der git-committer diesen Kontext erhalten, wäre der Weg von 20 Calls auf ~13 reduziert worden.

**Empfehlung:** Wenn der Main Agent weiß, dass ein pre-commit Hook wahrscheinlich fehlschlagen wird (z.B. bekannter `bd sync` Issue), diesen Hinweis im Dispatch-Prompt einschließen:
```
Note: pre-commit hook calls 'bd export' for bead sync. If commit fails with bd error: already handled.
```
