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
    p.add_argument("--neighbors", type=int, default=0,
                   help="Include N chunks before/after each match (0–2, default 0)")

    # ── search_hybrid ─────────────────────────────────────────────────────────
    p = sub.add_parser("search_hybrid", help="Hybrid search (vector + SPLADE + RRF fusion).")
    p.add_argument("query", help="Natural language search query")
    p.add_argument("collection", help="Collection to search in")
    p.add_argument("--top-k", dest="top_k", type=int, default=20,
                   help="Number of results (20–50, default 20)")
    p.add_argument("--document", default=None,
                   help="Filter by document name. %% as wildcard")
    p.add_argument("--neighbors", type=int, default=0,
                   help="Include N chunks before/after each match (0–2, default 0)")
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
    p = sub.add_parser("read_document", help="Read continuous chunks from a document.")
    p.add_argument("collection", help="Collection name")
    p.add_argument("document", help="Document name (e.g. 'chapter1.md')")
    p.add_argument("start_chunk", type=int, help="Chunk index to start reading from")
    p.add_argument("--num-chunks", dest="num_chunks", type=int, default=10,
                   help="Number of chunks to read (10–20, default 10)")

    # ── Dispatch ──────────────────────────────────────────────────────────────
    args = parser.parse_args()

    if args.cmd == "search":
        results = search_workflow(
            args.query, args.top_k, args.collection,
            args.document, min(args.neighbors, 2)
        )
        print(format_results(results))

    elif args.cmd == "search_hybrid":
        results = search_hybrid_workflow(
            args.query, args.top_k, args.collection,
            args.document, min(args.neighbors, 2), args.rerank
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
        num_chunks = max(args.num_chunks, 10)
        num_chunks = min(num_chunks, 20)
        result = read_document_workflow(
            args.collection, args.document, args.start_chunk, num_chunks
        )
        text = (
            f"Document: {result['document']} | "
            f"Chunks {result['start_chunk']}-{result['start_chunk'] + result['num_chunks'] - 1}"
            f"\n\n{result['content']}"
        )
        print(text)

    else:
        parser.error(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    main()
