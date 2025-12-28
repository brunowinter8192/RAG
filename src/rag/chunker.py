# INFRASTRUCTURE
import logging
import re
from pathlib import Path
from typing import Literal

logging.basicConfig(
    filename='src/rag/logs/chunker.log',
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


# Chunk by semantic boundaries (paragraphs, headers)
def chunk_semantic(content: str, chunk_size: int, overlap: int) -> list[str]:
    paragraphs = re.split(r'\n\n+', content)
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            overlap_text = current_chunk[-overlap:] if overlap > 0 else ""
            current_chunk = overlap_text + para
        else:
            current_chunk += "\n\n" + para if current_chunk else para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

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
