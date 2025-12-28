---
description: Clean a single markdown chunk from MinerU output
---

## Purpose

Clean and normalize a single markdown chunk. Called by /pdf-to-rag for each chunk after pre-cleanup.

**Note:** Structural fixes (fences, tables, newlines) are already done by postprocess.py. This agent handles semantic cleanup.

## Input

Caller provides: Single chunk content (not file path)

## Tasks

### 1. Semantic Clarity

- Fix unclear or broken sentences from PDF extraction
- Remove mid-word line breaks
- Fix hyphenation artifacts (e.g., "docu-\nment" → "document")

### 2. Residual Formatting

- Fix formatting that pre-cleanup missed
- Ensure consistent list markers
- Fix broken inline formatting (`**bold**`, `*italic*`)

### 3. Artifact Removal

- Remove page numbers, headers, footers
- Remove watermarks or repeated text
- Remove orphaned references (e.g., "[1]" without source)

### 4. Context Preservation

- Do NOT remove content that seems incomplete (chunk boundary)
- Do NOT add content that isn't there
- Preserve technical terms and code exactly

## Output

Return ONLY the cleaned chunk content.
No explanations, no markdown fences around output.
