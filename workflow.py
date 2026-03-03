# INFRASTRUCTURE
import argparse
import json
from pathlib import Path

from src.rag.chunker import chunk_workflow
from src.rag.indexer import index_json_workflow, delete_workflow
from src.rag.retriever import search_workflow


# ORCHESTRATOR
def main(command: str, **kwargs) -> None:
    if command == "index-json":
        count = index_json_workflow(kwargs["input"])
        print(f"Indexed {count} chunks from JSON")

    elif command == "search":
        results = search_workflow(
            kwargs["query"],
            kwargs.get("top_k", 5),
            collection=kwargs.get("collection"),
            document=kwargs.get("document")
        )
        for i, r in enumerate(results, 1):
            print(f"\n--- Result {i} (score: {r['score']}) ---")
            print(f"Collection: {r['collection']} | Document: {r['document']}")
            print(r['content'][:500])

    elif command == "chunk":
        chunks = chunk_workflow(kwargs["input"], kwargs.get("chunk_size", 1000), kwargs.get("overlap", 200))
        output = {
            "document": kwargs.get("document") or Path(kwargs["input"]).name,
            "chunks": [{"index": i, "content": c["content"]} for i, c in enumerate(chunks)]
        }
        json_path = Path(kwargs["input"]).with_suffix(".json")
        with open(json_path, "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Chunked {len(chunks)} chunks -> {json_path}")

    elif command == "delete":
        deleted = delete_workflow(
            collection=kwargs.get("collection"),
            document=kwargs.get("document")
        )
        print(f"Deleted {deleted} chunks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG System CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_json_parser = subparsers.add_parser("index-json", help="Index from chunks.json")
    index_json_parser.add_argument("--input", required=True, help="Path to chunks.json")

    search_parser = subparsers.add_parser("search", help="Search indexed documents")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    search_parser.add_argument("--collection", help="Filter by collection name")
    search_parser.add_argument("--document", help="Filter by document name")

    chunk_parser = subparsers.add_parser("chunk", help="Chunk markdown into JSON")
    chunk_parser.add_argument("--input", required=True, help="Path to markdown file")
    chunk_parser.add_argument("--chunk-size", type=int, default=1000, help="Target chunk size in chars")
    chunk_parser.add_argument("--overlap", type=int, default=200, help="Overlap between chunks in chars")
    chunk_parser.add_argument("--document", help="Document name (default: input filename)")

    delete_parser = subparsers.add_parser("delete", help="Delete indexed documents")
    delete_parser.add_argument("--collection", help="Delete by collection name")
    delete_parser.add_argument("--document", help="Delete by document name")

    args = parser.parse_args()
    main(args.command, **{k: v for k, v in vars(args).items() if k != "command"})
