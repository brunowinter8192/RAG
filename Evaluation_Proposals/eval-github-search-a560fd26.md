# Evaluation: github-search — agent-a560fd268e3556134

**Session:** 82d1d6ac-1b8b-4180-9db4-dab44a7dfe5b (RAG project, 2026-03-10 22:48-22:59)
**Agent:** github-research:github-search (Haiku)
**Task:** Research reranker model support in llama.cpp (ggml-org/llama.cpp)
**Result:** Erfolgreich — 5 Subtasks abgearbeitet, gute FILE/VALUE/EVIDENCE Ausgabe

---

## Scorecard

| KPI | Score | Begründung |
|-----|-------|-----------|
| Task Fulfillment | 93% | Alle 5 Subtasks abgedeckt. PR #20332 erwähnt ohne Quellenbeleg. |
| Tool Efficiency | 80% | 22 Calls. 3 wenig produktive Calls (#4 get_repo 241 chars, #14 README metadata_only 172 chars, #18 Qwen3-Reranker search 239 chars). 10-min Gap zwischen #12 und #13. |
| Format Compliance | 85% | Narrations-Intro vor Final Report verletzt explizite Regel. Summary-Section am Ende geht über FILE/VALUE/EVIDENCE Format hinaus. |
| Scope Control | 88% | Leicht über Scope (SUMMARY mit Empfehlungen), aber inhaltlich korrekt und nützlich. |
| Path Hygiene | 100% | Keine lokalen Pfade. |
| **Gesamt** | **88%** | |

**Ziel:** >85% ✓ (knapp erfüllt)

---

## Was gut lief

- Alle 5 Subtasks systematisch abgearbeitet (Issues, PRs, Code, Parameter, Qwen3-spezifisch)
- FILE/VALUE/EVIDENCE Format konsequent für alle Findings verwendet
- `repo:ggml-org/llama.cpp` Qualifier in allen Searches gesetzt (keine globalen Suchen)
- Issue Comments korrekt gelesen (#11 für Issue #16407 — die relevanteste Quelle)
- `grep_file` auf tools/server/README.md für offizielle Dokumentation
- Sehr hochwertige Synthese — ggerganov-Empfehlungen direkt zitiert

---

## Was schiefging

### Problem 1: Narration vor Final Report

Der Final Report beginnt mit:
> "I have enough information to provide a comprehensive research summary. Let me compile the findings now."

Das Agent-Definition sagt explizit:
> **"Wrong: 'Excellent! I found the issue. Let me get the details:' — This is an in-progress comment, NOT a final response."**

Der Agent liefert dann korrekte FILE/VALUE/EVIDENCE Blocks, aber der Intro-Satz verletzt die Regel. Wenn die Session an dieser Stelle abgebrochen wäre, wäre dieser Satz als "Final Response" erfasst worden — ohne jegliche Findings.

---

### Problem 2: Drei wenig produktive Calls

**Call #4: `get_repo` (241 chars)**
Der Task spezifizierte den Repo bereits. `get_repo` lieferte nur minimale Metadaten (Name, Beschreibung). Gemäß Agent-Definition: "If repo is already known (specified in task): skip search_repos, go directly to get_repo" — aber der Nutzen war hier marginal. Der Call ist laut Workflow erlaubt, aber die 241-char Ausgabe zeigt, dass nichts Wichtiges gewonnen wurde.

**Call #14: `get_file_content README.md metadata_only=True` (172 chars)**
Direkt nach Calls #12 (search_code) → Ergebnis: nur Datei-Metadaten (172 chars). Dann sofort Call #15 `get_repo_tree` — der eigentliche Struktur-Scan. Der metadata-only README-Call war redundant, da der repo_tree die gleiche Information (+ mehr) liefert.

**Call #18: `search_code "Qwen3-Reranker repo:ggml-org/llama.cpp"` (239 chars)**
Sehr kleine Ausgabe — wahrscheinlich 0 oder minimale Treffer. Suche nach dem Modell-Namen im Source-Code ist sinnvoll, aber 239 chars bedeutet fast keine Ergebnisse. Hätte early-terminated werden sollen.

---

### Problem 3: PR #20332 ohne Quellenbeleg

Im Final Report:
> **FILE:** PR #20332 (Open) - "Model fix qwen3vl reranker support"
> **EVIDENCE:** Recent PR labels: python

Nur "labels: python" als EVIDENCE — kein Inhalt, keine Commits, keine Beschreibung. Der Agent hat den PR nicht via `get_pr` gelesen, sondern nur aus der search_items-Ausgabe übernommen. Für einen FINDING-Block reicht das nicht.

---

### Problem 4: 10-Minuten-Gap zwischen Calls #12 und #13

Call #12: 22:48:34
Call #13: 22:59:33 (!) — **11 Minuten Pause**

Das ist kein Agent-Problem sondern wahrscheinlich eine externe Pause (User-Interrupt, System). Die Findings nach dem Gap (#13-22) sind qualitativ hochwertig — der Agent hat nach der Pause korrekt weitergemacht.

---

## Dispatch-Qualität

| Aspekt | Rating | Kommentar |
|--------|--------|-----------|
| Task Clarity | OK | Klare 5-Subtask-Struktur mit konkreten Suchbegriffen |
| Context Sufficiency | OK | Repo klar spezifiziert, Output-Format vorgegeben |
| Response Processing | OK | Main Agent hat die Findings korrekt verwendet (GitHub-Findings im Post-Dispatch-Summary) |

---

## Proposals

### Proposal 1: "Narration vor Final Report" — Härtere Warnung

**File:** `/Users/brunowinter2000/Documents/ai/Meta/ClaudeCode/MCP/github/agents/github-search.md`
**Location:** Section "Report Format — CRITICAL"

**WHY:** Die bestehende Regel nennt "Excellent! I found the issue. Let me get the details:" als falsches Beispiel. Der Agent hat aber ein subtil anderes Pattern verwendet: "I have enough information... Let me compile..." — das klingt nach Fortschritt, ist aber genau das gleiche Anti-Pattern. Haiku erkennt den Unterschied nicht.

**Current:**
```
Wrong: "Excellent! I found the issue. Let me get the details:" — This is an in-progress comment, NOT a final response.
Right: FILE: / VALUE: / EVIDENCE: blocks with synthesized findings.
```

**Proposed:**
```
Wrong: "Excellent! I found the issue. Let me get the details:" — in-progress comment, NOT final response.
Wrong: "I have enough information. Let me compile the findings now." — SAME anti-pattern, still not a report.
Wrong: "I'll now summarize what I found:" — transition sentences are forbidden before the report.
Right: Start DIRECTLY with FILE: / VALUE: / EVIDENCE: blocks. Zero intro text.
```

**Expected Impact:** Eliminiert alle Varianten des "transition before report" Anti-Patterns.

---

### Proposal 2: Evidence-Anforderung für PR-Findings

**File:** `/Users/brunowinter2000/Documents/ai/Meta/ClaudeCode/MCP/github/agents/github-search.md`
**Location:** Section "Output Requirements for Main Agent"

**WHY:** Der Agent hat PR #20332 nur mit "labels: python" als Evidence aufgenommen — das ist keine echte Evidence. Ein PR braucht mindestens seinen Titel, Status und eine kurze Beschreibung als Evidence.

**Current:**
```
FILE must be the full repo-relative path (from `get_repo_tree` output)
EVIDENCE must quote actual content from the file
```

**Proposed:** Ergänze nach der bestehenden Regel:
```
**For PRs and Issues:** EVIDENCE must include at minimum: title, status (open/closed/merged), and one concrete detail (description excerpt, key change, or comment). "labels: python" alone is insufficient Evidence — read the PR/Issue first.
```

**Expected Impact:** PRs werden gelesen (get_pr) bevor sie in den Report aufgenommen werden.
