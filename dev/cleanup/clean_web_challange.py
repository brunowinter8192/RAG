"""
Cleanup script for challange/ directory (5 files from HuggingFace + Gradio).

Two site types detected:

HuggingFace (huggingface.co_*):
  Two sub-types:
  A) Model page (black-forest-labs/FLUX.1-dev):
     Header noise: lines 3-38 (logo+nav, blank `# `, breadcrumb, tags, tabs,
       accept-conditions block, TOC list with anchor links)
     Content starts: line 40 (image + first paragraph)
     First real heading: "Key Features" on line 42
     Footer starts: "Downloads last month" (line 115)

  B) Docs pages (inference_client, inference-providers):
     Header noise: lines 3-43 (logo+nav, doc breadcrumb title, version selector,
       sidebar nav mega-lines, join-community promo, "Copy page")
     Content starts: first `#  [](url#anchor) Heading` line
     Footer: "Update on GitHub" + prev/next links (last 2 lines)

Gradio (www.gradio.app_*):
  Header noise: lines 3-120 (logo+top-nav, breadcrumb, "Use our Docs MCP",
    version selector, full sidebar nav list sections, "New to Gradio?",
    "Release History", prev/next placeholder)
  Content starts: first `# ComponentName` line
  Footer: inline prev/next nav + duplicate page TOC + "## Related Guides" section
    + Status/Twitter/GitHub footer line

Strategy:
  - Preserve `<!-- source: URL -->` comment on line 1.
  - Clean inline noise (anchor icon links, source links, parameter anchor links).
  - Clean anchor headings: "#  [ ](url) Title" -> "# Title"
"""

import re
from pathlib import Path

INPUT_DIR = Path(__file__).parent.parent.parent / "data" / "documents" / "challange"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def extract_source_comment(lines):
    if lines and lines[0].startswith("<!-- source:"):
        return lines[0].rstrip("\n")
    return None


def strip_trailing_blanks(lines):
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def build_output(source_comment, content_lines):
    content_lines = strip_trailing_blanks(list(content_lines))
    result = []
    if source_comment:
        result.append(source_comment + "\n")
        result.append("\n")
    result.extend(content_lines)
    if result and not result[-1].endswith("\n"):
        result[-1] += "\n"
    return result


# ---------------------------------------------------------------------------
# HuggingFace inline cleaners
# ---------------------------------------------------------------------------

# "#  [ ](url#anchor) Title " -> "# Title"
RE_HF_ANCHOR_HEADING = re.compile(r'^(#{1,6})\s+\[ \]\([^)]*\)\s*(.*)')
# "[< source >](url)" inline
RE_HF_SOURCE_LINK = re.compile(r'\[\s*<\s*source\s*>\s*\]\([^)]+\)')
# "[ ](url#anchor)" inline icon anchor — NOT image syntax
RE_HF_INLINE_ANCHOR = re.compile(r'(?<!!)\[ \]\([^)]*#[^)]*\)\s*')
# "[](url)" inline empty anchor (parameter anchors) — NOT image syntax "![](...)"
RE_HF_PARAM_ANCHOR = re.compile(r'(?<!!)\[\]\(https://huggingface\.co[^)]*\)\s*')


def clean_hf_line(line):
    # Convert anchor headings to plain headings
    m = RE_HF_ANCHOR_HEADING.match(line)
    if m:
        level = m.group(1)
        title = m.group(2).strip()
        line = f"{level} {title}\n" if title else f"{level}\n"
    else:
        line = RE_HF_SOURCE_LINK.sub("", line)
        line = RE_HF_INLINE_ANCHOR.sub("", line)
        line = RE_HF_PARAM_ANCHOR.sub("", line)
    return line


# ---------------------------------------------------------------------------
# HuggingFace Model page (e.g. black-forest-labs/FLUX.1-dev)
# ---------------------------------------------------------------------------

# TOC items: "  * [Title](url#anchor "Title")"
RE_HF_TOC_ITEM = re.compile(r'^\s+\*\s+\[.+?\]\(https://huggingface\.co/[^)]*#')

# Header noise line patterns for model pages
RE_HF_LOGO = re.compile(r'^\[!\[Hugging Face')
RE_HF_ICON_NAV = re.compile(r'^\s+\*\s+(\[\]\(https://huggingface\.co/(models|datasets|spaces|docs|enterprise)\)|\[new\]|\[Pricing\]|\[Log In\]|\[Sign Up\]|\* \* \*)')
RE_HF_MODEL_BREADCRUMB = re.compile(r'^\[ !\[')  # "[ ![avatar](...)  ](...)"
RE_HF_TAGS_LINE = re.compile(r'^\[ Text-to-Image \]|^\[ Diffusers \]|^License: ')
RE_HF_TABS_LINE = re.compile(r'Files Files and versions')
RE_HF_ACCEPT = re.compile(r'(This repository is publicly accessible|By clicking .Agree|'
                           r'\[Log in\]\(https://huggingface\.co/login\?next|'
                           r'\[Sign Up\]\(https://huggingface\.co/join\?next)')
RE_HF_FOLLOW = re.compile(r'^(like \d|Follow$)')
RE_HF_AVATAR_IMG = re.compile(r'^!\[\]\(https://cdn-avatars\.huggingface\.co/')

# Footer: model page
RE_HF_MODEL_FOOTER = re.compile(r'^Downloads last month')


def cleanup_hf_model(lines):
    """Clean HuggingFace model page."""
    source_comment = extract_source_comment(lines)

    # The header noise occupies lines 3-38 (0-indexed: 2-37).
    # Content starts after the TOC list ends (after the blank heading + breadcrumb block).
    # Strategy: skip until we pass all TOC items and header noise lines,
    # then take everything until the footer.

    in_header = True
    content_start = 1  # default fallback

    for i, line in enumerate(lines):
        if i == 0:
            continue

        stripped = line.strip()

        if in_header:
            # Skip known header noise
            if not stripped:
                continue
            if RE_HF_LOGO.match(line):
                continue
            if RE_HF_ICON_NAV.match(line):
                continue
            # Blank heading "# " — model page artifact
            if re.match(r'^#\s*$', stripped):
                continue
            # Model breadcrumb lines (avatar link, org/model name, slash, like count, follow)
            if RE_HF_MODEL_BREADCRUMB.match(line):
                continue
            if stripped in ('/', 'Follow', 'like 12.5k', 'like') or RE_HF_FOLLOW.match(stripped):
                continue
            if RE_HF_AVATAR_IMG.match(line):
                continue
            # Check if it's a name line like "[black-forest-labs](url)"
            if re.match(r'^\[[\w-]+\]\(https://huggingface\.co/[\w-]+\)\s*$', stripped):
                continue
            if re.match(r'^\[[\w.\d-]+\]\(https://huggingface\.co/[\w-]+/[\w.\d-]+\)\s*$', stripped):
                continue
            # Tags line
            if RE_HF_TAGS_LINE.match(line):
                continue
            # Tabs line
            if RE_HF_TABS_LINE.search(line):
                continue
            # Accept conditions block
            if RE_HF_ACCEPT.search(line):
                continue
            # TOC items
            if RE_HF_TOC_ITEM.match(line):
                continue
            # "Black Forest Labs 35k" type line (org name + follower count)
            if re.match(r'^!\[\]\(https://cdn-avatars', line):
                continue
            # Detected end of header — this is content
            in_header = False
            content_start = i

        if not in_header:
            break

    # Find footer start
    footer_start = len(lines)
    for i in range(content_start, len(lines)):
        if RE_HF_MODEL_FOOTER.match(lines[i]):
            footer_start = i
            break

    content_lines = [clean_hf_line(l) for l in lines[content_start:footer_start]]
    return build_output(source_comment, content_lines)


# ---------------------------------------------------------------------------
# HuggingFace Docs pages
# ---------------------------------------------------------------------------

RE_HF_VIEW_ALL_DOCS = re.compile(r'🏡 View all docs')
RE_HF_VERSION_SELECTOR = re.compile(r'^main v\d+\.\d+')
RE_HF_VERSION_SIMPLE = re.compile(r'^main (EN|CN|DE|FR|HI|KO|TM)?\s*$')
RE_HF_GITHUB_ICON = re.compile(r'^\[\]\(https://github\.com/')
RE_HF_JOIN_PROMO = re.compile(
    r'^(Join the Hugging Face community|and get access to the augmented|'
    r'Collaborate on models, datasets|Faster examples with accelerated|'
    r'Switch between documentation themes|to get started|Copy page)'
)
RE_HF_JOIN_LOGO = re.compile(r'^!\[Hugging Face.s logo\]')

# Sidebar nav sections: long lines with many consecutive doc links
# These appear as single lines with multiple "[Text ](url)" patterns
RE_HF_SIDEBAR_MEGA = re.compile(r'(\]\(https://huggingface\.co/docs/){3,}')

# Section headers that appear in sidebar nav (plain text on their own line)
HF_SIDEBAR_SECTION_LABELS = {
    "Get started", "How-to guides", "Conceptual guides", "Reference",
    "Guides", "Providers", "Inference Tasks", "Other Tasks", "Integrations",
    "Get Started", "Hub API", "Register as an Inference Provider",
    "Search documentation",
}

# Docs page footer
RE_HF_DOCS_FOOTER = re.compile(r'^\[Update on GitHub\]')
# Prev/next nav at end: "[←Title](url) [Title→](url)"
RE_HF_DOCS_PREVNEXT = re.compile(r'^\[←|^\[←.*\]\(|→\]\(')


def is_hf_docs_header_noise(line, stripped):
    """Return True if line is header noise in a HF docs page."""
    if RE_HF_LOGO.match(line):
        return True
    if RE_HF_ICON_NAV.match(line):
        return True
    if RE_HF_VIEW_ALL_DOCS.search(line):
        return True
    if RE_HF_VERSION_SELECTOR.match(stripped):
        return True
    if RE_HF_VERSION_SIMPLE.match(stripped):
        return True
    if RE_HF_GITHUB_ICON.match(line):
        return True
    if RE_HF_JOIN_PROMO.match(stripped):
        return True
    if RE_HF_JOIN_LOGO.match(line):
        return True
    if stripped == "Copy page":
        return True
    if stripped == "`⌘K`":
        return True
    # Known sidebar section labels
    if stripped in HF_SIDEBAR_SECTION_LABELS:
        return True
    # Mega-line with 3+ doc links = sidebar nav
    if RE_HF_SIDEBAR_MEGA.search(line):
        return True
    # Breadcrumb label lines (plain text, no markup)
    # e.g. "Hub Python Library documentation", "Inference Providers documentation"
    if re.match(r'^[A-Z][A-Za-z ]+documentation$', stripped):
        return True
    return False


def cleanup_hf_docs(lines):
    """Clean HuggingFace documentation page."""
    source_comment = extract_source_comment(lines)

    # HF docs structure:
    #   logo+nav → "DocTitle documentation" → "DocTitle" → "# DocTitle"
    #   → "🏡 View all docs..." → sidebar nav mega-lines → join promo → "Copy page"
    #   → ACTUAL CONTENT STARTS
    # "Copy page" is the reliable end-of-header marker.
    # After "Copy page", the next non-blank line is the actual content.

    content_start = 1
    copy_page_found = False

    for i, line in enumerate(lines):
        if i == 0:
            continue
        stripped = line.strip()
        if not copy_page_found:
            if stripped == "Copy page":
                copy_page_found = True
            continue
        # After "Copy page", skip blank lines
        if not stripped:
            continue
        # First non-blank line after "Copy page" = content
        content_start = i
        break

    # Fallback: if "Copy page" not found, use original noise-detection approach
    if not copy_page_found:
        in_header = True
        for i, line in enumerate(lines):
            if i == 0:
                continue
            stripped = line.strip()
            if in_header:
                if not stripped:
                    continue
                if is_hf_docs_header_noise(line, stripped):
                    continue
                in_header = False
                content_start = i
            if not in_header:
                break

    # Find footer
    footer_start = len(lines)
    for i in range(content_start, len(lines)):
        if RE_HF_DOCS_FOOTER.match(lines[i]):
            footer_start = i
            break

    content_lines = [clean_hf_line(l) for l in lines[content_start:footer_start]]
    return build_output(source_comment, content_lines)


# ---------------------------------------------------------------------------
# Gradio cleanup
# ---------------------------------------------------------------------------

RE_GRADIO_LOGO = re.compile(r'^\[!\[Gradio logo\]')
RE_GRADIO_DOCS_MCP = re.compile(r'^Use our \[Docs MCP\]')
RE_GRADIO_VERSION = re.compile(r'^\d+\.\d+\.\d+\s+\d+\.\d+\.\d+')
RE_GRADIO_SIDEBAR_LINK = re.compile(r'^\s+\*\s+\[.+?\]\(https://www\.gradio\.app/docs/')
RE_GRADIO_NEW_TO = re.compile(r'^New to Gradio\?')
RE_GRADIO_RELEASE_HISTORY = re.compile(r'^See the \[Release History\]')
RE_GRADIO_PREVNEXT = re.compile(r'^\[.*←.*\]|^\[.*→.*\]|^←|^→')
# Sidebar section header labels (appear as "## Section" lines in the nav)
GRADIO_SIDEBAR_SECTIONS = {
    "## Building Demos", "## Blocks Layout", "## Components", "## Helpers",
    "## Modals", "## Routes", "## Other",
}

# Inline anchor SVG icon: [![](svg_url)](anchor_url)
RE_GRADIO_ANCHOR_ICON = re.compile(
    r'\[!\[\]\(https://raw\.githubusercontent\.com/gradio-app/gradio/[^)]+anchor\.svg\)\]\([^)]+\)'
)

# Top-level nav line: "[API](...) [Guides](...) [HTML Components](...)"
RE_GRADIO_TOP_NAV_LINE = re.compile(r'\[API\]\(https://www\.gradio\.app/docs\)')

GRADIO_PLAIN_NOISE = {"Community", "Search CTRL+K"}

# Footer guide link line: "[GuideTitle](url)[GuideTitle2](url)" with no other text
RE_GRADIO_FOOTER_GUIDE_LINKS = re.compile(
    r'^\[([A-Z][^\]]+)\]\(https://www\.gradio\.app/guides/'
)


def is_gradio_header_noise(line, stripped):
    if RE_GRADIO_LOGO.match(line):
        return True
    if RE_GRADIO_TOP_NAV_LINE.search(line):
        return True
    if stripped in GRADIO_PLAIN_NOISE:
        return True
    if RE_GRADIO_DOCS_MCP.match(line):
        return True
    if RE_GRADIO_VERSION.match(stripped):
        return True
    # Breadcrumb numbered list (e.g. "  1. Components ")
    if re.match(r'^\s+\d+\.\s+', line):
        return True
    if stripped in GRADIO_SIDEBAR_SECTIONS:
        return True
    if RE_GRADIO_SIDEBAR_LINK.match(line):
        return True
    if RE_GRADIO_NEW_TO.match(line):
        return True
    if RE_GRADIO_RELEASE_HISTORY.match(line):
        return True
    if RE_GRADIO_PREVNEXT.match(stripped):
        return True
    return False


def clean_gradio_line(line):
    """Remove inline SVG anchor icon links."""
    return RE_GRADIO_ANCHOR_ICON.sub("", line)


def cleanup_gradio(lines):
    source_comment = extract_source_comment(lines)

    # Find first real heading: "# ComponentName" (capital letter)
    content_start = 1
    in_header = True

    for i, line in enumerate(lines):
        if i == 0:
            continue
        stripped = line.strip()
        if in_header:
            if not stripped:
                continue
            if is_gradio_header_noise(line, stripped):
                continue
            # First non-noise, non-blank line = content start
            in_header = False
            content_start = i

        if not in_header:
            break

    # Find footer by forward scan:
    # Footer starts at the first occurrence of any of these AFTER real content:
    #   - Inline prev/next link like "[ ← HTML ](...) [ ImageEditor → ](...)"
    #   - "[Status](..." line (site footer)
    #   - "## Related Guides" section
    #   - The repeated page TOC: "[Image](url#image)" top-level anchor
    # These all appear AFTER the last real content paragraph.
    # We use a two-pass: find all candidate footer-start lines, pick the earliest
    # one that is followed only by noise.

    # Pattern for the inline prev/next nav line that signals end of content
    RE_GRADIO_INLINE_PREVNEXT = re.compile(r'\[ ← .* \]|\[ .* → \]')
    RE_GRADIO_STATUS_LINE = re.compile(r'^\[Status\]\(https://status\.gradio\.app\)')
    RE_GRADIO_PAGE_TOC = re.compile(r'^\[.+?\]\(https://www\.gradio\.app/docs/gradio/[^)]+#[^)]+\)$')
    RE_GRADIO_RELATED_GUIDES = re.compile(r'^## Related Guides')

    footer_start = len(lines)
    for i in range(content_start, len(lines)):
        stripped = lines[i].strip()
        if RE_GRADIO_STATUS_LINE.match(stripped):
            footer_start = i
            break
        if RE_GRADIO_RELATED_GUIDES.match(stripped):
            footer_start = i
            break
        # Inline prev/next nav line (signals end of content)
        if RE_GRADIO_INLINE_PREVNEXT.search(stripped) and i > content_start + 5:
            footer_start = i
            # But check if the previous non-blank line is the footer guide links line
            for j in range(i - 1, max(i - 3, content_start - 1), -1):
                if lines[j].strip():
                    if RE_GRADIO_FOOTER_GUIDE_LINKS.match(lines[j].strip()):
                        footer_start = j
                    break
            break
        if RE_GRADIO_PAGE_TOC.match(stripped) and i > content_start + 5:
            # TOC appears right after the inline nav; walk back to find the nav line
            for j in range(i - 1, max(i - 5, content_start - 1), -1):
                if lines[j].strip():
                    if RE_GRADIO_INLINE_PREVNEXT.search(lines[j]):
                        footer_start = j
                        # Check if guide links line precedes the nav
                        for k in range(j - 1, max(j - 3, content_start - 1), -1):
                            if lines[k].strip():
                                if RE_GRADIO_FOOTER_GUIDE_LINKS.match(lines[k].strip()):
                                    footer_start = k
                                break
                    else:
                        footer_start = i
                    break
            break

    content_lines = [clean_gradio_line(l) for l in lines[content_start:footer_start]]
    return build_output(source_comment, content_lines)


# ---------------------------------------------------------------------------
# Main dispatcher
# ---------------------------------------------------------------------------

def is_hf_model_page(filename):
    """Detect HF model page vs docs page by URL structure."""
    # Model pages: huggingface.co_{org}_{model-name}.md
    # Docs pages: huggingface.co_docs_*
    return "huggingface.co_" in filename and "_docs_" not in filename


def process_file(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    name = path.name
    if name.startswith("huggingface.co_"):
        if is_hf_model_page(name):
            cleaned = cleanup_hf_model(lines)
        else:
            cleaned = cleanup_hf_docs(lines)
    elif name.startswith("www.gradio.app_"):
        cleaned = cleanup_gradio(lines)
    else:
        # Unknown site — return unchanged
        return text, text

    return text, "".join(cleaned)


def main():
    md_files = sorted(INPUT_DIR.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {INPUT_DIR}")
        return

    total_before = 0
    total_after = 0

    for path in md_files:
        before_text, after_text = process_file(path)
        before_chars = len(before_text)
        after_chars = len(after_text)
        total_before += before_chars
        total_after += after_chars
        reduction = (1 - after_chars / before_chars) * 100 if before_chars else 0
        print(f"  {path.name}: {before_chars} -> {after_chars} chars ({reduction:.1f}% reduction)")
        path.write_text(after_text, encoding="utf-8")

    total_reduction = (1 - total_after / total_before) * 100 if total_before else 0
    print(f"\nFILES PROCESSED: {len(md_files)}")
    print(f"Total chars before: {total_before}")
    print(f"Total chars after:  {total_after}")
    print(f"Total reduction:    {total_reduction:.1f}%")


if __name__ == "__main__":
    main()
