# INFRASTRUCTURE
import argparse

# From src/rag/indexer.py: Index documents into vector DB
from src.rag.indexer import index_workflow

# From src/rag/retriever.py: Search vector DB
from src.rag.retriever import search_workflow


# ORCHESTRATOR
def main(command: str, **kwargs) -> None:
    if command == "index":
        count = index_workflow(kwargs["input_dir"], kwargs.get("patterns"))
        print(f"Indexed {count} chunks")

    elif command == "search":
        results = search_workflow(kwargs["query"], kwargs.get("top_k", 5))
        for i, r in enumerate(results, 1):
            print(f"\n--- Result {i} (score: {r['score']}) ---")
            print(f"Source: {r['source']}")
            print(r['content'][:500])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG System CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index", help="Index documents")
    index_parser.add_argument("--input-dir", required=True, help="Directory to index")
    index_parser.add_argument("--patterns", nargs="+", default=None, help="File patterns")

    search_parser = subparsers.add_parser("search", help="Search indexed documents")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--top-k", type=int, default=5, help="Number of results")

    args = parser.parse_args()
    main(args.command, **{k: v for k, v in vars(args).items() if k != "command"})
