# INFRASTRUCTURE
import logging
import re
from pathlib import Path
from typing import Literal

LOG_DIR = Path(__file__).parent / "logs"

logging.basicConfig(
    filename=LOG_DIR / "chunker.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_OVERLAP = 200


# ORCHESTRATOR
def chunk_workflow(
    file_path: str,
    strategy: Literal["semantic", "code", "fixed"] = "semantic",
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP
) -> list[dict]:
    content = load_file(file_path)
    file_type = detect_file_type(file_path)

    if strategy == "code" or file_type == "code":
        chunks = chunk_code(content)
    elif strategy == "semantic" or file_type == "markdown":
        chunks = chunk_semantic(content, chunk_size, overlap)
    else:
        chunks = chunk_fixed(content, chunk_size, overlap)

    enriched = enrich_chunks(chunks, file_path)
    logging.info(f"Chunked {file_path}: {len(enriched)} chunks ({strategy})")
    return enriched


# FUNCTIONS

# Load file content
def load_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


# Detect file type from extension
def detect_file_type(file_path: str) -> Literal["code", "markdown", "text"]:
    ext = Path(file_path).suffix.lower()
    if ext in ['.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.rb']:
        return "code"
    elif ext in ['.md', '.markdown']:
        return "markdown"
    return "text"


# Chunk by semantic boundaries with sentence-awareness
def chunk_semantic(content: str, chunk_size: int, overlap: int) -> list[str]:
    separators = ["\n\n", "\n", ". ", "! ", "? ", " "]
    splits = recursive_split(content, separators, chunk_size)
    return merge_with_overlap(splits, chunk_size, overlap)


# Recursively split text using hierarchical separators
def recursive_split(text: str, separators: list[str], chunk_size: int) -> list[str]:
    if len(text) <= chunk_size or not separators:
        return [text] if text.strip() else []

    sep = separators[0]
    remaining_seps = separators[1:]

    parts = text.split(sep)
    result = []

    for i, part in enumerate(parts):
        if i < len(parts) - 1:
            part = part + sep

        if len(part) <= chunk_size:
            result.append(part)
        else:
            result.extend(recursive_split(part, remaining_seps, chunk_size))

    return result


# Merge small splits into chunks with overlap
def merge_with_overlap(splits: list[str], chunk_size: int, overlap: int) -> list[str]:
    if not splits:
        return []

    chunks = []
    current = ""

    for split in splits:
        if len(current) + len(split) <= chunk_size:
            current += split
        else:
            if current.strip():
                chunks.append(current.strip())
            overlap_text = current[-overlap:] if overlap > 0 and current else ""
            current = overlap_text + split

    if current.strip():
        chunks.append(current.strip())

    return chunks


# Chunk code by function/class definitions
def chunk_code(content: str) -> list[str]:
    patterns = [
        r'(^def\s+\w+.*?(?=\n(?:def\s|class\s|$)))',
        r'(^class\s+\w+.*?(?=\n(?:def\s|class\s|$)))',
        r'(^function\s+\w+.*?(?=\n(?:function\s|class\s|$)))',
        r'(^const\s+\w+\s*=\s*(?:async\s*)?\(.*?(?=\n(?:const\s|function\s|class\s|$)))',
    ]

    chunks = []
    remaining = content

    for pattern in patterns:
        matches = re.findall(pattern, remaining, re.MULTILINE | re.DOTALL)
        chunks.extend(matches)

    if not chunks:
        return chunk_fixed(content, DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP)

    return [c.strip() for c in chunks if c.strip()]


# Chunk by fixed size with overlap
def chunk_fixed(content: str, chunk_size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0

    while start < len(content):
        end = start + chunk_size
        chunk = content[start:end]

        if end < len(content):
            last_space = chunk.rfind(' ')
            if last_space > chunk_size * 0.5:
                chunk = chunk[:last_space]
                end = start + last_space

        chunks.append(chunk.strip())
        start = end - overlap if overlap > 0 else end

    return chunks


# Add metadata to chunks
def enrich_chunks(chunks: list[str], file_path: str) -> list[dict]:
    return [
        {
            "content": chunk,
            "source": file_path,
            "chunk_index": i,
            "total_chunks": len(chunks)
        }
        for i, chunk in enumerate(chunks)
    ]
