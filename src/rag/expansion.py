# INFRASTRUCTURE

from .db import fetch_chunk_range


# FUNCTIONS

# Expand results with neighboring chunks, deduplicated and merged
def expand_results(conn, results: list[dict], neighbors: int) -> list[dict]:
    groups = group_by_document(results, neighbors)
    expanded = []

    for (collection, document), group_data in groups.items():
        ranges = find_contiguous_ranges(group_data['indices'])
        hit_scores = group_data['hit_scores']

        for start_idx, end_idx in ranges:
            chunks = fetch_chunk_range(conn, collection, document, start_idx, end_idx)
            range_score = max(
                (score for idx, score in hit_scores.items() if start_idx <= idx <= end_idx),
                default=0
            )
            expanded.append({
                'content': merge_chunks(chunks),
                'collection': collection,
                'document': document,
                'chunk_index': start_idx,
                'chunk_end': end_idx,
                'score': range_score
            })

    expanded.sort(key=lambda r: (r['collection'], r['document'], r['chunk_index']))
    return expanded


# Merge chunks with overlap deduplication
def merge_chunks(chunks: list[dict]) -> str:
    if not chunks:
        return ""

    result = chunks[0]['content']
    for i in range(1, len(chunks)):
        overlap = find_overlap(result, chunks[i]['content'])
        result += "\n\n" + chunks[i]['content'][overlap:]
    return result


# Find longest suffix of text1 that is prefix of text2
def find_overlap(text1: str, text2: str, max_overlap: int = 300) -> int:
    for size in range(min(len(text1), len(text2), max_overlap), 0, -1):
        if text1[-size:] == text2[:size]:
            return size
    return 0


# Group results by document and collect all needed indices with hit scores
def group_by_document(results: list[dict], neighbors: int) -> dict:
    groups = {}
    for r in results:
        key = (r['collection'], r['document'])
        if key not in groups:
            groups[key] = {'indices': set(), 'hit_scores': {}}

        idx = r['chunk_index']
        groups[key]['hit_scores'][idx] = r['score']
        for i in range(max(0, idx - neighbors), idx + neighbors + 1):
            groups[key]['indices'].add(i)

    return groups


# Find contiguous ranges from a set of indices
def find_contiguous_ranges(indices: set) -> list[tuple]:
    if not indices:
        return []

    sorted_indices = sorted(indices)
    ranges = []
    start = sorted_indices[0]
    end = start

    for idx in sorted_indices[1:]:
        if idx == end + 1:
            end = idx
        else:
            ranges.append((start, end))
            start = idx
            end = idx

    ranges.append((start, end))
    return ranges
