#!/usr/bin/env python3
import os
import sys

# Ensure src.rag.* imports resolve regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse

from src.rag.retriever import (
    search_workflow, format_results,
    search_keyword_workflow,
    search_hybrid_workflow,
    list_collections_workflow, format_collections,
    list_documents_workflow, format_documents,
    read_document_workflow
)


def main():
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="RAG CLI — semantic, hybrid, and keyword search over indexed document collections."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # ── search ────────────────────────────────────────────────────────────────
    p = sub.add_parser("search", help="Semantic (dense vector) search.")
    p.add_argument("query", help="Natural language search query")
    p.add_argument("collection", help="Collection to search in")
    p.add_argument("--top-k", dest="top_k", type=int, default=20,
                   help="Number of results (20–50, default 20)")
    p.add_argument("--document", default=None,
                   help="Filter by document name. %% as wildcard (e.g. 'arxiv_%%')")

    # ── search_hybrid ─────────────────────────────────────────────────────────
    p = sub.add_parser("search_hybrid", help="Hybrid search (vector + SPLADE + RRF fusion).")
    p.add_argument("query", help="Natural language search query")
    p.add_argument("collection", help="Collection to search in")
    p.add_argument("--top-k", dest="top_k", type=int, default=20,
                   help="Number of results (20–50, default 20)")
    p.add_argument("--document", default=None,
                   help="Filter by document name. %% as wildcard")
    p.add_argument("--no-rerank", dest="rerank", action="store_false", default=True,
                   help="Disable cross-encoder reranking (faster, lower precision)")

    # ── search_keyword ────────────────────────────────────────────────────────
    p = sub.add_parser("search_keyword", help="BM25 keyword search for exact terms.")
    p.add_argument("query", help="Keywords (space = AND). Case insensitive, stems words.")
    p.add_argument("collection", help="Collection to search in")
    p.add_argument("--top-k", dest="top_k", type=int, default=20,
                   help="Number of results (20–50, default 20)")
    p.add_argument("--document", default=None,
                   help="Filter by document name. %% as wildcard")

    # ── list_collections ──────────────────────────────────────────────────────
    sub.add_parser("list_collections", help="List all indexed collections with chunk counts.")

    # ── list_documents ────────────────────────────────────────────────────────
    p = sub.add_parser("list_documents", help="List documents in a collection.")
    p.add_argument("collection", help="Collection name")
    p.add_argument("--document", default=None,
                   help="Filter by document name. %% as wildcard")

    # ── read_document ─────────────────────────────────────────────────────────
    p = sub.add_parser("read_document", help="Read anchor chunk plus N before and M after.")
    p.add_argument("collection", help="Collection name")
    p.add_argument("document", help="Document name (e.g. 'chapter1.md')")
    p.add_argument("chunk_index", type=int, help="Anchor chunk index")
    p.add_argument("--before", type=int, default=0,
                   help="Chunks to read before the anchor (0–10, default 0)")
    p.add_argument("--after", type=int, default=0,
                   help="Chunks to read after the anchor (0–10, default 0)")

    # ── Dispatch ──────────────────────────────────────────────────────────────
    args = parser.parse_args()

    if args.cmd == "search":
        results = search_workflow(
            args.query, args.top_k, args.collection, args.document
        )
        print(format_results(results))

    elif args.cmd == "search_hybrid":
        results = search_hybrid_workflow(
            args.query, args.top_k, args.collection, args.document, args.rerank
        )
        print(format_results(results))

    elif args.cmd == "search_keyword":
        results = search_keyword_workflow(
            args.query, args.top_k, args.collection, args.document
        )
        print(format_results(results))

    elif args.cmd == "list_collections":
        results = list_collections_workflow()
        print(format_collections(results))

    elif args.cmd == "list_documents":
        results = list_documents_workflow(args.collection, args.document)
        print(format_documents(results))

    elif args.cmd == "read_document":
        before = min(max(args.before, 0), 10)
        after = min(max(args.after, 0), 10)
        result = read_document_workflow(
            args.collection, args.document, args.chunk_index, before, after
        )
        start = result['chunk_index'] - result['before']
        end = result['chunk_index'] + result['after']
        text = (
            f"Document: {result['document']} | "
            f"Chunks {start}-{end} (anchor: {result['chunk_index']})"
            f"\n\n{result['content']}"
        )
        print(text)

    else:
        parser.error(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    main()
