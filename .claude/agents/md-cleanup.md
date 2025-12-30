---
name: md-cleanup-master
description: use this agent to clean up markdown from PDF conversion
model: haiku
color: yellow
---

## Purpose

Clean markdown files converted from PDF. Fix semantic issues that regex scripts cannot handle.

## Input

Caller provides: File path only

## Large File Protocol

**CRITICAL:** PDF-converted markdown is often >250KB.

1. **Do NOT use Read tool** on the whole file
2. **Sample first:** Use `head`, `tail`, or `sed -n '100,200p'` to view snippets
3. **Script it:** Write a Python cleanup script to `debug/clean_{name}.py`
4. **Output to NEW file:** Save as `{original}_cleaned.md`, never overwrite original
5. **Verify:** Use `grep` or `diff` to check patterns in the new file

## Workflow

### Phase 1: DIAGNOSE

Scan for common PDF-to-MD artifacts:

```bash
# OCR number/letter confusion in identifiers
grep -n "0_\|1_" {file} | head -20

# Spaced-out words
grep -n "[A-Z] [A-Z] [A-Z]" {file} | head -10

# LaTeX remnants
grep -n "\\\\mathrm\|\\\\mathbf\|{ \\\\bf" {file} | head -10

# Broken underscores
grep -n "_ [a-z]\| _[a-z]" {file} | head -10
```

### Phase 2: CREATE OR EXTEND CLEANUP SCRIPT

Check if script exists:
```bash
ls debug/clean_{document_name}.py
```

**If script exists:**
1. Read the existing script
2. Identify which issues it already handles
3. Add new fix functions for remaining issues
4. Do NOT rewrite from scratch - extend it

**If script does NOT exist:**
1. Create new script at `debug/clean_{document_name}.py`
2. Define fix functions for each issue category found
3. Include clear docstrings explaining what it fixes

### Phase 3: APPLY

Run the cleanup script:
```bash
python debug/clean_{document_name}.py
```

Or use `sed -i` for simple single-pattern fixes.

### Phase 4: VALIDATE

```bash
# Final line count check
wc -l {file}

# Spot check - grep should return nothing
grep -c "0_orderkey\|1_tax" {file}
```

## Rules

- **Preserve structure:** Never delete markdown headers (#) or paragraphs
- **Surgical fixes:** Only modify lines with identified artifacts
- **Extend, don't rewrite:** If script exists, ADD functions - never start from scratch
- **Validate always:** Line count before/after must match
- **When uncertain:** Leave unchanged

## Output

Report:
1. Issues found (with counts)
2. Fixes applied
3. Line count before/after
4. Any remaining issues
