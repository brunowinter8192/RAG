---
name: agent-web-md-cleanup
description: Dispatch rules for web-md-cleanup agent
---

# Web MD Cleanup Agent Dispatch

## Agent Info

| Agent | subagent_type | Model | Output |
|-------|---------------|-------|--------|
| web-md-cleanup | `web-md-cleanup` | Haiku | Patterns detected, files processed, char reduction |

## When to Use

After website crawling (crawl_site.py or similar) produces raw markdown files with navigation, footers, and UI chrome.

## Script Location

Agents create scripts in `{project_root}/cleanup/`. This folder is gitignored and exempt from code standards.

## How to Prompt

```
Clean up the website-crawled markdown files in this directory.

INPUT DIRECTORY: {directory_path}
All .md files in this directory are raw crawl4ai output with website chrome.

Sample 3-5 files first to identify common navigation/footer patterns,
then build a single cleanup script that processes all files.
```

## After Agent Returns

1. **Char reduction check:** Total reduction should be 10-50%. Less than 5% = agent missed patterns. More than 60% = agent may have removed content.
2. **Spot-check:** Read the first 20 lines of 2-3 cleaned files. Should start with content heading, not navigation.
3. **Source comment check:** `grep "<!-- source:" {dir}/*.md | wc -l` should equal file count (comments preserved).
4. If content was removed: revert and re-run with feedback.

## Iteration

If patterns remain after first run:
- Re-run agent with specific feedback: "Footer still present in files X, Y. Pattern: [example lines]"
- Agent extends the cleanup script
- Repeat until spot-check passes
