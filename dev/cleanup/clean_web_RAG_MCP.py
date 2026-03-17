"""
Cleanup script for RAG_MCP website-crawled markdown files.
Removes navigation, cookie banners, site headers/footers while preserving content.
Skips files matching arxiv__*.md (PDF-converted papers, not web crawls).

Sites covered:
  - www.anthropic.com
  - docs.together.ai
  - weaviate.io
  - research.trychroma.com
  - www.crunchydata.com (+ German cookie consent)
  - www.pinecone.io (+ German cookie UI)
  - medium.com (404 page — entirely noise)
  - developer.nvidia.com (404 page)
  - anthropic.com/docs
  - docs.haystack.deepset.ai
  - docs.vectorchord.ai
  - docs.voyageai.com
  - www.thenile.dev
  - zilliz.com
"""

import re
from pathlib import Path

INPUT_DIR = Path(__file__).parent.parent.parent / "data" / "documents" / "RAG_MCP"


# ---------------------------------------------------------------------------
# 404 / error page detection
# ---------------------------------------------------------------------------

ERROR_PAGE_MARKERS = [
    'PAGE NOT FOUND',
    '## 404',
    'Out of nothing, something.',
    '# Not Found\nSorry, but the page',
    '# Not Found',
    # Zilliz 404
    '# 404\n## Page Not Found',
    "Oops! It looks like you've taken a wrong turn",
]


def is_error_page(content_lines: list[str]) -> bool:
    """Detect if this crawled page is a 404 or error page with no real content."""
    # Check within first 40 lines
    sample = '\n'.join(content_lines[:40])
    for marker in ERROR_PAGE_MARKERS:
        if marker in sample:
            return True
    return False


# ---------------------------------------------------------------------------
# Header removal helpers
# ---------------------------------------------------------------------------

def find_content_start(lines: list[str]) -> int:
    """Return index of first # heading. Falls back to 0 if no heading found."""
    for i, l in enumerate(lines):
        if re.match(r'^# ', l):
            return i
    return 0


# ---------------------------------------------------------------------------
# Site-specific footer detection
# ---------------------------------------------------------------------------

# Each entry is (pattern, is_regex). When a line matches, everything from
# that line to EOF is removed.
# IMPORTANT: patterns that appear early in the file (like sidebar nav) must NOT
# be footer triggers — only patterns that appear AFTER the main content.
FOOTER_TRIGGERS = [
    # Anthropic site footer (NOTE: ### Resources / ### Company also appear in crunchydata nav,
    # so these are handled in POST_CONTENT_FOOTER_TRIGGERS below instead)
    # (r'^### Resources\s*$', True),  -- moved to post-content
    # (r'^### Company\s*$', True),    -- moved to post-content
    # Weaviate: "Newer Post" / "Older Post" blog navigation (appears right after content)
    (r'\[Newer Post ', False),
    (r'\[Older Post ', False),
    # Chroma footer
    (r'^\[Try Chroma Cloud\]', True),
    (r'^Chroma is the open-source search', False),
    # CrunchyData German cookie consent footer
    (r'^## Datenschutz-Präferenz-Center\s*$', True),
    # Pinecone: share links section
    (r'^Share:\s*$', True),
    # Together.ai footer logo block - NOTE: this also appears in the header (line ~6),
    # so it is handled in POST_CONTENT_FOOTER_TRIGGERS below instead.
    # (r'^\[Together AI Docs home page', True),  -- moved to post-content
    # Generic copyright lines
    (r'^© \d{4} ', True),
    (r'^Copyright © \d{4}', True),
    # Zilliz / generic: "Related Articles" or "Related Resources" at end
    (r'^## Related Articles\s*$', True),
    (r'^## Related Resources\s*$', True),
    # NVidia / thenile: "Related content" blocks
    (r'^## Related content\s*$', True),
    # Pinecone chapter list / series nav (after content)
    (r'^\[Product Quantization\].*\[Next Post', False),
    # Medium 404 footer
    (r'To make Medium work, we log user data', False),
    # Generic doc site footers with social icon links
    (r'img/discord\.svg', False),
    # Haystack footer: "Previous ... Next ..." navigation line at bottom
    (r'\[Previous .+\]\[Next .+\]', False),
    (r'^\[Previous ', True),
    # Haystack deepset footer "Was this page helpful" + "On this page" = duplicated TOC
    # Only trigger "On this page" if it appears AFTER a heading (i.e., as footer TOC)
    # We handle this via a post-heading-only scan in find_footer_start_after_content()
]

# Footer triggers that are only valid AFTER real content has started
# (to avoid removing sidebar "Was this page helpful?" which appears before content in docs)
POST_CONTENT_FOOTER_TRIGGERS = [
    (r'Was this page helpful\?', False),
    (r'^On this page\s*$', True),
    # Together.ai footer logo block (also appears in header, so must be post-content only)
    (r'^\[Together AI Docs home page', True),
    # Anthropic site footer (### Resources / ### Company also appear in crunchydata nav header)
    (r'^### Resources\s*$', True),
    (r'^### Company\s*$', True),
]


def find_footer_start(lines: list[str], content_start: int) -> int:
    """Return index where footer begins, or len(lines) if no footer found.

    content_start: the line index where actual content (# heading) starts.
    Post-content triggers are only checked after content_start.
    """
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Check always-on footer triggers
        for pattern, is_regex in FOOTER_TRIGGERS:
            if is_regex:
                if re.search(pattern, stripped):
                    return i
            else:
                if pattern in stripped:
                    return i
        # Check post-content triggers (only valid after content starts)
        if i > content_start:
            for pattern, is_regex in POST_CONTENT_FOOTER_TRIGGERS:
                if is_regex:
                    if re.search(pattern, stripped):
                        return i
                else:
                    if pattern in stripped:
                        return i
    return len(lines)


# ---------------------------------------------------------------------------
# Header noise removal (before the first # heading)
# ---------------------------------------------------------------------------

# Lines in the header region that should be dropped.
# These patterns are ONLY applied to lines BEFORE the first # heading.
HEADER_NOISE_PATTERNS = [
    # Skip links
    r'^\[Skip to ',
    # Bare logo link (line that is just a link with no text or an image link to home)
    r'^\[\]\(https?://',
    r'^\[!\[.*logo.*\]',
    r'^\[!\[.*Logo.*\]',
    r'!\[logo\]',
    r'!\[Logo\]',
    # Anthropic top nav
    r'^\[Try Claude\]',
    r'^\[Engineering at Anthropic\]',
    # Cookie banner content (weaviate cookiebot popup)
    r'This website uses cookies',
    r'We use cookies to enable',
    r'We use essential cookies',
    r'cookie consent',
    r'Consent Selection',
    r'\*\*Necessary\*\*',
    r'\*\*Preferences\*\*',
    r'\*\*Statistics\*\*',
    r'\*\*Marketing\*\*',
    r'\*\*Targeting\*\*',
    r'Maximum Storage Duration',
    r'HTTP Cookie',
    r'HTML Local Storage',
    r'Pixel Tracker',
    r'\[Cookiebot',
    r'CookieConsent',
    r'Cookiebot',
    r'\[Google\d',
    r'\[HubSpot',
    r'\[LinkedIn\d',
    r'\[beehiiv',
    r'\[client\.px-cloud',
    r'__cf_bm',
    r'_pxvid',
    r'pxcts',
    r'_cfuvid',
    r'_px3\b',
    r'cf_clearance',
    r'li_gc',
    r'bcookie',
    r'cookietest',
    r'rc::[a-z]',
    r'_GRECAPTCHA',
    r'test_cookie',
    r'#GPC_BANNER_ICON',
    r'#GPC_TOAST_TEXT',
    r'#IABV2SETTINGS',
    r'\[#GPC_',
    r'\[#IAB',
    r'Show details',
    r'Necessary cookies help make',
    r'Performance cookies',
    r'Functional cookies',
    r'Marketing cookies',
    r'Targeting cookies',
    r'Powered by Onetrust',
    r'Powered byThis documentation is built',
    # Cookie consent UI (German — pinecone, crunchydata)
    r'Öffnet in einem neuen Fenster',
    r'wesentliche Cookies',
    r'Einstellungen verwalten',
    r'Alle akzeptieren',
    r'wesentliche Cookies ablehnen',
    r'Cookie-Einstellungen schließen',
    r'Cookie-Richtlinie',
    r'Dieses Dialogfeld schließen',
    # Navigation breadcrumbs / search bars
    r'^Search\.\.\.\s*$',
    r'^⌘K\s*$',
    r'^Navigation\s*$',
    r'^Search`K`\s*$',
    r'^Search\s*`K`',
    # Medium top nav
    r'^\[Sitemap\]',
    r'^\[Open in app\]',
    r'^Sign up\s*$',
    r'^\[Sign in\]',
    r'^\[Medium Logo\]',
    r'^Get app\s*$',
    r'^\[Search\]',
    # Pinecone promo banner
    r'🚀 Pinecone BYOC',
    # Haystack version selector
    r'^\[2\.\d+',
    r'^\* \[2\.\d+',
    r'^\* \[1\.x archived',
    r'^\* \[2\.x archived',
    # Site-wide nav list items that are clearly just nav (link to another page, no context)
    # Anthropic nav items
    r'^\s*\* \[Research\]\(https://www\.anthropic\.com',
    r'^\s*\* \[Economic Futures\]\(',
    r'^\s*\* \[News\]\(https://www\.anthropic\.com',
    # Weaviate header nav (before article heading)
    r'^\s*\* \[Consent\]\(https://weaviate\.io',
    r'^\s*\* \[Details\]\(https://weaviate\.io',
    r'^\s*\* \[About\]\(https://weaviate\.io',
    r'Some of the data collected by this provider',
    r'\*\*embed/v3/counters\.gif\*\*',
    r'^g2\.com\s*$',
    r'^hubapi\.com\s*$',
    # Together.ai sidebar nav lines (section headers)
    r'^##### Agents\s*$',
    r'^##### Apps\s*$',
    r'^##### General Guides\s*$',
    r'^##### Dedicated Containers\s*$',
    r'^##### Search & RAG\s*$',
    # Haystack nav items in sidebar (version picker, API Reference, etc.)
    r'^\[Docs\]\(https://docs\.haystack',
    r'^\[API Reference\]\(https://docs\.haystack',
    r'^\[Contribute\]\(',
    r'^\[GitHub\]\(https://github\.com/deepset',
    # VectorChord nav
    r'^\[VectorChord\]\(',
    r'^Search`',
    # Chroma technical report header
    r'^Table of Contents\s*$',
    r'^\[Chroma Technical Report\]',
    # Together.ai cookie banner (specific)
    r'PreferencesDeclineAccept',
]

HEADER_NOISE_RE = re.compile('|'.join(HEADER_NOISE_PATTERNS), re.IGNORECASE)


def is_header_noise(line: str) -> bool:
    return bool(HEADER_NOISE_RE.search(line))


# ---------------------------------------------------------------------------
# Full pre-heading block removal for certain sites
# ---------------------------------------------------------------------------

# For sites where the ENTIRE pre-heading section is navigation,
# we can just drop everything before the first # heading entirely.
FULL_HEADER_STRIP_DOMAINS = [
    'weaviate_io',
    'www_anthropic_com',
    'anthropic__docs',
    'docs_together_ai',
    'docs_haystack_deepset_ai',
    'docs_vectorchord_ai',
    'docs_voyageai_com',
    'www_pinecone_io',
    'www_crunchydata_com',
    'www_thenile_dev',
    'zilliz_com',
    'medium_com',
    'developer_nvidia_com',
    'research_trychroma_com',
]


def should_strip_full_header(path: Path) -> bool:
    name = path.stem.lower()
    return any(domain in name for domain in FULL_HEADER_STRIP_DOMAINS)


# ---------------------------------------------------------------------------
# Core cleanup logic
# ---------------------------------------------------------------------------

def clean_file(path: Path) -> tuple[int, int]:
    """Clean a single file in-place. Returns (chars_before, chars_after)."""
    text = path.read_text(encoding='utf-8')
    chars_before = len(text)

    lines = text.splitlines(keepends=True)

    # Preserve the source comment (always line 1 if present)
    source_comment = ''
    start_idx = 0
    if lines and lines[0].startswith('<!-- source:'):
        source_comment = lines[0].rstrip('\n')
        start_idx = 1
        # Skip blank line after source comment
        if start_idx < len(lines) and lines[start_idx].strip() == '':
            start_idx += 1

    content_lines = [l.rstrip('\n') for l in lines[start_idx:]]

    # Handle 404/error pages — entire file is noise
    if is_error_page(content_lines):
        result = source_comment + '\n\n<!-- NOTE: This page returned an error (404). No content available. -->\n'
        path.write_text(result, encoding='utf-8')
        return chars_before, len(result)

    # 1. Find first # heading
    content_start = find_content_start(content_lines)

    # 2. Find footer boundary (only after content start for ambiguous patterns)
    footer_start = find_footer_start(content_lines, content_start)
    content_lines = content_lines[:footer_start]

    # Recalculate content_start after footer trim
    content_start = find_content_start(content_lines)

    # 3. Strip pre-heading region
    pre_heading = content_lines[:content_start]
    post_heading = content_lines[content_start:]

    if should_strip_full_header(path):
        # Drop entire pre-heading block (it's all nav for these sites)
        cleaned_pre = []
        # If no # heading was found (content_start==0), filter post_heading for noise.
        # If nothing meaningful remains, mark as no-content.
        if content_start == 0 and not any(re.match(r'^# ', l) for l in post_heading):
            # Check if there's any substantive content (non-nav, non-blank lines > 80 chars)
            substantive = [l for l in post_heading if len(l.strip()) > 80 and not is_header_noise(l)]
            if not substantive:
                result = source_comment + '\n\n<!-- NOTE: No content heading found. Page may be nav-only or content was paywalled. -->\n'
                path.write_text(result, encoding='utf-8')
                return chars_before, len(result)
    else:
        # For other sites (e.g. research.trychroma.com): keep pre-heading but remove noise
        cleaned_pre = [l for l in pre_heading if not is_header_noise(l)]
        # Collapse multiple blank lines
        collapsed = []
        for l in cleaned_pre:
            if l.strip() == '' and (not collapsed or collapsed[-1].strip() == ''):
                continue
            collapsed.append(l)
        cleaned_pre = collapsed
        # Strip trailing blanks
        while cleaned_pre and cleaned_pre[-1].strip() == '':
            cleaned_pre.pop()

    # 4. Remove trailing blank lines from post_heading
    while post_heading and post_heading[-1].strip() == '':
        post_heading.pop()

    # 5. Reassemble
    parts = []
    if source_comment:
        parts.append(source_comment)
    if cleaned_pre:
        parts.append('')
        parts.extend(cleaned_pre)
    parts.append('')
    parts.extend(post_heading)

    result = '\n'.join(parts) + '\n'
    path.write_text(result, encoding='utf-8')
    return chars_before, len(result)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    files = sorted([
        f for f in INPUT_DIR.glob('*.md')
        if not f.name.startswith('arxiv__')
    ])

    if not files:
        print(f'No files found in {INPUT_DIR}')
        return

    total_before = 0
    total_after = 0

    for f in files:
        before, after = clean_file(f)
        total_before += before
        total_after += after
        reduction = (before - after) / before * 100 if before > 0 else 0
        print(f'  {f.name}: {before:,} -> {after:,} ({reduction:.1f}%)')

    overall_reduction = (total_before - total_after) / total_before * 100 if total_before > 0 else 0
    print()
    print(f'FILES PROCESSED: {len(files)}')
    print(f'Total chars before: {total_before:,}')
    print(f'Total chars after:  {total_after:,}')
    print(f'Reduction: {overall_reduction:.1f}%')


if __name__ == '__main__':
    main()
