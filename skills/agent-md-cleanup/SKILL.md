---
name: agent-md-cleanup
description: Dispatch rules for md-cleanup-master agent
---

# MD Cleanup Agent Dispatch

## Agent Info

| Agent | subagent_type | Model | Output |
|-------|---------------|-------|--------|
| md-cleanup-master | `md-cleanup-master` | Haiku | Issues found, fixes applied, word count |

## When to Use

After PDF-to-markdown conversion when postprocess.py has run but semantic issues remain.

## Script Location

Agents create scripts in `{project_root}/debug/`. This folder is gitignored and exempt from code standards.

## How to Prompt

**Goal: Clean artifacts but PRESERVE content integrity.**
It is better to leave a split word unfixed than to merge two separate words.

```
Clean up the raw markdown file produced from a PDF conversion.

INPUT: {input_filepath}
OUTPUT: {output_filepath}
```

**With known issues (faster):**
```
Known issues:
- OCR: [describe specific patterns found]
- LaTeX: [describe remnants]
```

## After Agent Returns

1. **Word count check:** Compare input vs output word count (must be stable +/- 1%)
2. **Run-on word check:** `grep -oE '\b(isthe|tothe|ofthe|inthe|iscentral)\b' {cleaned_file}`
3. If run-on words found: re-run agent (iteration) or manual fix
4. If word count stable AND no run-on words: done

## Iteration

If remaining issues after first run:
- Re-run agent with same prompt
- Agent analyzes remaining issues, extends relevant fix scripts
- Repeat until all issue counts reach 0
