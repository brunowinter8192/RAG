#!/usr/bin/env python3
"""
docs_drift_check.py — Detect documentation drift in the RAG project.

Three sequential checks:
  1. Path-Existence : referenced file/dir paths exist on disk
  2. LOC-Drift      : claimed LOC in DOCS.md headings match actual wc -l
  3. Symbol-Existence: identifiers from docs are found in source code

Exit code: 0 = clean (0 findings), 1 = drift detected (≥1 findings).

Design notes:
- OldThemes/ is excluded from the symbol check (historical state docs intentionally
  mention removed identifiers — e.g. old function names like _get_free_port() that
  were renamed to _resolve_port(). Flagging those is by-design false-positive noise).
- Paths starting with ~/ are skipped (user-home references, not project-local).
- Paths with runtime extensions (.log, .flock, .pid) are skipped (gitignored artifacts).
- Paths inside fenced code blocks are skipped (bash/python usage examples with
  template paths like data/documents/MyCollection/).
- For relative path references (e.g. OldThemes/foo.md inside a decisions/ file),
  resolution is attempted both from project root AND from the doc's own directory.
"""

# INFRASTRUCTURE
import argparse
import datetime
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Scan scope for all three checks
DOC_GLOBS = [
    "decisions/**/*.md",
    "**/DOCS.md",
    "sources/sources.md",
]

# Source code scope for symbol grep
SOURCE_GLOBS = ["src/**/*.py", "dev/**/*.py"]
SOURCE_ROOT_FILES = ["cli.py", "workflow.py", "start.sh"]

# Symbol check: OldThemes documents historical/superseded state; removed identifiers
# appear there intentionally. Only scan current-state docs for symbol existence.
SYMBOL_SCAN_EXCLUDES = {"decisions/OldThemes"}

# Runtime-only file extensions — gitignored, never checked in the worktree
RUNTIME_SKIP_EXTENSIONS = {".log", ".flock", ".pid"}

# LOC heading pattern: ### module.py (N LOC)
LOC_HEADING = re.compile(r"^###\s+([\w.-]+\.py)\s+\((\d+)\s+LOC\)")

# Path-like token: requires at least one directory component, allows * wildcards
PATH_PATTERN = re.compile(
    r"(?:[a-zA-Z0-9_.*-]+/)+[a-zA-Z0-9_.*-]+"
    r"(?:\.(?:py|md|json|sh|yaml|yml|txt))?"
    r"(?::\d+)?"
)

# Symbol patterns
ALL_CAPS_RE = re.compile(r"\b[A-Z][A-Z0-9_]{3,}\b")
SNAKE_FUNC_RE = re.compile(r"\b([a-z_][a-z0-9_]*)\(\)")

WHITELIST_FILE = Path(__file__).resolve().parent / "docs_drift_whitelist.txt"


# ORCHESTRATOR
def main() -> None:
    args = parse_args()
    whitelist = load_whitelist(WHITELIST_FILE)
    doc_files = collect_doc_files(PROJECT_ROOT)
    source_files = collect_source_files(PROJECT_ROOT)

    path_findings = check_path_existence(doc_files, PROJECT_ROOT)
    loc_findings = check_loc_drift(doc_files, PROJECT_ROOT)
    symbol_findings = check_symbol_existence(doc_files, PROJECT_ROOT, whitelist, source_files)

    print_report(path_findings, loc_findings, symbol_findings, args.verbose)

    total = len(path_findings) + len(loc_findings) + len(symbol_findings)
    sys.exit(0 if total == 0 else 1)


# FUNCTIONS

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Detect documentation drift: path existence, LOC accuracy, symbol presence.",
        epilog="Exit code: 0 = clean, 1 = drift detected.",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show all checked items, not just findings.",
    )
    return p.parse_args()


def load_whitelist(path: Path) -> set[str]:
    if not path.exists():
        return set()
    entries = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            entries.add(line)
    return entries


def collect_doc_files(root: Path) -> list[Path]:
    seen: set[Path] = set()
    result: list[Path] = []
    for pattern in DOC_GLOBS:
        for p in sorted(root.glob(pattern)):
            if p not in seen:
                seen.add(p)
                result.append(p)
    return result


def collect_source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in SOURCE_GLOBS:
        files.extend(sorted(root.glob(pattern)))
    for name in SOURCE_ROOT_FILES:
        p = root / name
        if p.exists():
            files.append(p)
    return files


def _toggle_fence(line: str, in_fence: bool) -> bool:
    stripped = line.strip()
    if stripped.startswith("```") or stripped.startswith("~~~"):
        return not in_fence
    return in_fence


def _should_skip_path(raw: str, root: Path, doc_dir: Path) -> bool:
    """Return True when this path token should be excluded from the existence check."""
    if raw.startswith(("http://", "https://")):
        return True
    if raw.startswith("~/"):
        return True
    if "{" in raw:  # template variable (e.g. server-port-{N}.json)
        return True
    path_part = re.sub(r":\d+$", "", raw)  # strip :line_anchor
    ext = Path(path_part.split("*")[0]).suffix.lower()
    if ext in RUNTIME_SKIP_EXTENSIONS:
        return True
    # First path component must exist somewhere reachable (project root or doc dir)
    first = path_part.split("/")[0]
    if not (root / first).exists() and not (doc_dir / first).exists():
        return True
    return False


def check_path_existence(doc_files: list[Path], root: Path) -> list[tuple]:
    """Check 1 — referenced file/dir paths exist on disk."""
    findings: list[tuple] = []
    for doc in doc_files:
        in_fence = False
        for lineno, line in enumerate(doc.read_text(errors="replace").splitlines(), 1):
            in_fence = _toggle_fence(line, in_fence)
            if in_fence:
                continue

            # Collect candidates: backtick-quoted strings + bare PATH_PATTERN matches
            candidates: list[str] = re.findall(r"`([^`]+)`", line)
            for m in PATH_PATTERN.finditer(line):
                candidates.append(m.group(0))

            seen: set[str] = set()
            for raw in candidates:
                raw = raw.strip()
                if raw in seen:
                    continue
                seen.add(raw)
                if not PATH_PATTERN.search(raw):
                    continue
                if _should_skip_path(raw, root, doc.parent):
                    continue

                path_str = re.sub(r":\d+$", "", raw)
                rel_doc = str(doc.relative_to(root))

                if "*" in path_str:
                    # Glob pattern — try from root and doc parent
                    hits = list(root.glob(path_str)) + list(doc.parent.glob(path_str))
                    if not hits:
                        findings.append((f"{rel_doc}:{lineno}", path_str, "NOT FOUND (glob)"))
                else:
                    # Direct existence — try from root and doc parent
                    if not (root / path_str).exists() and not (doc.parent / path_str).exists():
                        findings.append((f"{rel_doc}:{lineno}", path_str, "NOT FOUND"))
    return findings


def check_loc_drift(doc_files: list[Path], root: Path) -> list[tuple]:
    """Check 2 — DOCS.md claimed LOC matches actual newline count (wc -l equivalent)."""
    findings: list[tuple] = []
    for doc in doc_files:
        if doc.name != "DOCS.md":
            continue
        module_dir = doc.parent
        for lineno, line in enumerate(doc.read_text(errors="replace").splitlines(), 1):
            m = LOC_HEADING.match(line)
            if not m:
                continue
            module_name = m.group(1)
            claimed = int(m.group(2))
            module_path = module_dir / module_name
            if not module_path.exists():
                continue  # file may be documented but not yet created
            actual = module_path.read_text(errors="replace").count("\n")
            drift = abs(claimed - actual)
            if drift >= 5:
                rel_doc = str(doc.relative_to(root))
                rel_mod = str(module_path.relative_to(root))
                findings.append((f"{rel_doc}:{lineno}", rel_mod, claimed, actual, drift))
    return findings


def check_symbol_existence(
    doc_files: list[Path],
    root: Path,
    whitelist: set[str],
    source_files: list[Path],
) -> list[tuple]:
    """Check 3 — identifiers from docs are present in source code."""
    source_text = "\n".join(f.read_text(errors="replace") for f in source_files)

    findings: list[tuple] = []
    checked: set[str] = set()

    for doc in doc_files:
        rel = str(doc.relative_to(root))
        if any(rel.startswith(exc) for exc in SYMBOL_SCAN_EXCLUDES):
            continue

        in_fence = False
        for lineno, line in enumerate(doc.read_text(errors="replace").splitlines(), 1):
            in_fence = _toggle_fence(line, in_fence)
            # Symbols are checked even inside code blocks (they should exist in source)

            for sym in ALL_CAPS_RE.findall(line):
                if sym in whitelist or sym in checked:
                    continue
                checked.add(sym)
                if not re.search(rf"\b{re.escape(sym)}\b", source_text):
                    findings.append((f"{rel}:{lineno}", sym, "ALL_CAPS not found in src"))

            for m in SNAKE_FUNC_RE.finditer(line):
                sym = m.group(1)
                if sym in whitelist or sym in checked:
                    continue
                checked.add(sym)
                if not re.search(rf"\b{re.escape(sym)}\b", source_text):
                    findings.append((f"{rel}:{lineno}", f"{sym}()", "function not found in src"))

    return findings


def print_report(
    path_findings: list[tuple],
    loc_findings: list[tuple],
    symbol_findings: list[tuple],
    verbose: bool = False,
) -> None:
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    total = len(path_findings) + len(loc_findings) + len(symbol_findings)

    print(f"# Docs Drift Check — {ts}")
    print(f"\nProject root: {PROJECT_ROOT}")
    print(f"\n## Summary\n")
    print(f"- Path-Drift:   {len(path_findings)} findings")
    print(f"- LOC-Drift:    {len(loc_findings)} findings")
    print(f"- Symbol-Drift: {len(symbol_findings)} findings")
    print(f"- Total:        {total}")

    print(f"\n## Path-Drift ({len(path_findings)} findings)\n")
    if not path_findings:
        print("None — all paths exist.")
    else:
        for loc, path, status in path_findings:
            print(f"- `{loc}` references `{path}` — {status}")

    print(f"\n## LOC-Drift ({len(loc_findings)} findings)\n")
    if not loc_findings:
        print("None — all LOC counts accurate.")
    else:
        for loc, module, claimed, actual, drift in loc_findings:
            sign = "+" if actual > claimed else ""
            print(f"- `{loc}` claims `{module}` = {claimed} LOC, actual {actual} ({sign}{actual - claimed})")

    print(f"\n## Symbol-Drift ({len(symbol_findings)} findings)\n")
    if not symbol_findings:
        print("None — all symbols found in source.")
    else:
        for loc, sym, reason in symbol_findings:
            print(f"- `{loc}` symbol `{sym}` — {reason}")

    if verbose and total == 0:
        print("\n## Verbose: Scan Complete\nAll checks passed — no findings.")


if __name__ == "__main__":
    main()
