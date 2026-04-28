# INFRASTRUCTURE


# FUNCTIONS

# Format search results for display
def format_results(results: list[dict]) -> str:
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"--- Result {i} (score: {r['score']}) ---")
        if 'chunk_end' in r and r['chunk_end'] != r['chunk_index']:
            chunk_info = f"Chunks: {r['chunk_index']}-{r['chunk_end']}"
        else:
            chunk_info = f"Chunk: {r['chunk_index']}"
        lines.append(f"Collection: {r['collection']} | Document: {r['document']} | {chunk_info}")
        lines.append(r['content'])
        lines.append("")
    return "\n".join(lines)


# Format collections list for display
def format_collections(results: list[dict]) -> str:
    if not results:
        return "No collections indexed."
    lines = ["Indexed Collections:", ""]
    for r in results:
        lines.append(f"  {r['collection']} ({r['chunks']} chunks)")
    return "\n".join(lines)


# Format documents list for display
def format_documents(results: list[dict]) -> str:
    if not results:
        return "No documents in this collection."
    lines = ["Documents:", ""]
    for r in results:
        lines.append(f"  {r['document']} ({r['chunks']} chunks)")
    return "\n".join(lines)
