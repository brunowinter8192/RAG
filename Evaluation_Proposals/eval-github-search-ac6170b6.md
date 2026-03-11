# Evaluation: github-search — agent-ac6170b6d96af61cc (INCOMPLETE SESSION)

**Session:** 82d1d6ac-1b8b-4180-9db4-dab44a7dfe5b (RAG project, 2026-03-10 23:07)
**Agent:** github-research:github-search (Haiku)
**Task:** Deep dive into reranker issues in ggml-org/llama.cpp — 6 Subtasks
**Result:** FAILED — 3 von 6 Subtasks abgearbeitet, keine Synthese, Abbruch

---

## Scorecard

| KPI | Score | Begründung |
|-----|-------|-----------|
| Task Fulfillment | 25% | 3/6 Issues gefetched, aber keine Synthese. Subtasks 4-6 (Engagement-Sort, Mungert/QuantFactory-Search, 8B-Search) nicht durchgeführt. |
| Tool Efficiency | 30% | 3 Calls — aber unvollständig. Kein Search-by-engagement, kein Code-Search. |
| Format Compliance | 5% | Kein FILE/VALUE/EVIDENCE Output. Final Response = Intro-Text nach den Tool-Calls. |
| Scope Control | N/A | Session abgebrochen |
| Path Hygiene | 100% | Keine lokalen Pfade |
| **Gesamt** | **25%** | |

**Ziel:** >85%

---

## Was schiefging

### Problem 1: "I'll start by fetching" — geschrieben NACH den Tool-Calls

Die Tool Call Summary zeigt 3 Calls um 23:07:42-43. Das Final Response lautet:

> "I'll dive into the llama.cpp reranker-related issues systematically. Let me start by fetching the specific issues you mentioned."

Dieser Text wurde NACH den 3 Tool-Calls generiert — d.h. der Agent hat die Issues bereits gefetched, dann aber eine Planungs-Aussage geschrieben, als hätte er noch nicht begonnen.

Das ist ein Haiku-Kontextverlust-Pattern: nach großen Tool-Outputs (Issue #16407 hatte ~3900 chars mit langen Code-Snippets) verliert Haiku den Überblick über was bereits getan wurde und restarts mental.

Dies verletzt die Regel: **"CRITICAL: Start with a tool call IMMEDIATELY. Your FIRST output MUST be a tool call — not a sentence, not a plan, not 'I'll search...'"** — implizit aber auch: Planungs-Text nach Tool-Calls ist genauso schädlich, da er als "Final Response" erfasst wird wenn die Session endet.

---

### Problem 2: Zu viele Subtasks in einem einzigen Dispatch

Der Task-Prompt enthielt **6 Subtasks:**
1. Issue #16407 — Datum, Kommentare, GGUF-Provider, Fix-Datum
2. Issue #19756 — Datum, Status, betroffene Modelle
3. Issue #17743 — Datum, Auflösung
4. **Suche ALLE Issues nach "rerank", sortiert nach Engagement**
5. **Suche Issues zu Mungert/QuantFactory GGUF**
6. **Suche Issues zu Qwen3-Reranker-8B spezifisch**

Nach 3 Calls (Subtasks 1-3) wurde der Session-State erschöpft. Subtasks 4-6 wurden nie ausgeführt.

Haiku hat ein effektives Kontext-Budget von ~15-20 signifikanten Tool-Calls bevor die Qualität degradiert. 6 Subtasks mit je 1-3 Calls = 6-18 erwartete Calls. Das ist grenzwertig.

**Root cause ist Dispatcher-seitig:** 6 Subtasks in einem einzelnen Agent-Dispatch ist zu viel. Der Dispatcher hätte die Tasks aufteilen sollen: Subtasks 1-3 (bekannte Issues) als erster Dispatch, Subtasks 4-6 (Suche/Exploration) als zweiter.

---

### Problem 3: Synthese fehlt vollständig

Selbst für die 3 abgearbeiteten Issues (alle gefetched, korrekte Daten vorhanden) gab es keine Synthese im FILE/VALUE/EVIDENCE-Format. Der Agent hat die Issues gelesen aber nie die Information zusammengestellt.

Dies ist direkt mit Problem 1 verbunden: der Kontextverlust nach großen Outputs führte dazu, dass der Agent neu "plante" statt zu synthetisieren.

---

## Dispatch-Qualität

| Aspekt | Rating | Kommentar |
|--------|--------|-----------|
| Task Clarity | OK | Jeder Subtask ist klar definiert mit konkreten Issue-Nummern |
| Context Sufficiency | Poor | 6 Subtasks für einen einzigen Haiku-Agent. Subtasks 4-6 erfordern Search-Calls zusätzlich zu den 3 Issue-Fetches → zu viel für ein Agent-Budget |
| Response Processing | N/A | Agent hat keine auswertbare Antwort geliefert |

**Root cause link:** Die schlechte Task Fulfillment (25%) ist DIREKT auf die Dispatch-Qualität zurückzuführen. Der Dispatcher hat zu viele Tasks in einen Dispatch gepackt.

---

## Proposals

### Proposal 1: Max-Subtask-Regel für github-search Dispatches

**File:** `/Users/brunowinter2000/Documents/ai/Meta/ClaudeCode/MCP/github/skills/github/SKILL.md`
**Location:** Section über Subagent Dispatch (existierende Dispatch-Anleitung)

**WHY:** Haiku-Agents degradieren bei >4 Subtasks. 6 Subtasks in einem Dispatch überschreiten das effektive Kontext-Budget, besonders wenn Tool-Outputs groß sind (Issue-Bodies mit langen Reproduktionsschritten).

**Current:** (keine explizite Subtask-Limit-Regel in SKILL.md vorhanden)

**Proposed:** Füge zur Dispatch-Guidance hinzu:
```
**Subtask Limit (CRITICAL):**
- Maximum 3-4 subtasks per github-search dispatch
- If task requires 5+ subtasks: split into sequential dispatches
- Example split: "Dispatch A: fetch known issues #X, #Y, #Z" → "Dispatch B: search by engagement + provider-specific queries"
- Reason: Haiku context budget exhausts after ~15-20 large tool outputs
```

**Expected Impact:** Verhindert unvollständige Sessions durch zu viele Tasks pro Dispatch.

---

### Proposal 2: Haiku Context Recovery — Explicit Synthesis Trigger

**File:** `/Users/brunowinter2000/Documents/ai/Meta/ClaudeCode/MCP/github/agents/github-search.md`
**Location:** Section "DATA, not plans (CRITICAL)" oder neuer Abschnitt

**WHY:** Nach großen Tool-Outputs verliert Haiku den Überblick und schreibt Planungs-Text statt zu synthetisieren. Ein expliziter Trigger am Ende jeder "data collection phase" hilft.

**Current:**
```
**DATA, not plans (CRITICAL):** Your job is to READ files and RETURN data. Never return a "strategy" or "plan" describing what you WOULD do.
```

**Proposed:** Ergänze:
```
**DATA, not plans (CRITICAL):** Your job is to READ files and RETURN data. Never return a "strategy" or "plan" describing what you WOULD do.

**After every 3 tool calls:** Pause and write a 1-line self-check:
"Completed: [list what's done]. Remaining: [list what's not done yet]."
This prevents context drift where Haiku restarts planning after large outputs.

**CRITICAL:** Never write "I'll start by..." or "Let me now..." AFTER you have already made tool calls. If you have data, SYNTHESIZE. If you have not yet made calls, make them IMMEDIATELY (no planning text).
```

**Expected Impact:** Reduziert Haiku-Kontextverlust-Pattern. Agent synthetisiert Zwischenergebnisse statt neu zu planen.
