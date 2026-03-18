import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from .base import BaseRetriever


class RerankerRetriever(BaseRetriever):
    """Wraps any retriever and reranks results with cross-encoder."""

    def __init__(self, base_retriever: BaseRetriever, top_n: int = 50):
        self.base = base_retriever
        self.top_n = top_n

    def name(self) -> str:
        return f"{self.base.name()}+Rerank"

    def search(self, corpus: dict, queries: dict, top_k: int) -> dict[str, dict[str, float]]:
        base_results = self.base.search(corpus, queries, self.top_n)

        from src.rag.reranker import rerank_documents
        from src.rag.server_manager import ensure_ready
        ensure_ready("reranker")

        reranked = {}
        for qid, doc_scores in base_results.items():
            query_text = queries[qid]
            candidates = []
            doc_ids = []
            for doc_id in doc_scores:
                if doc_id in corpus:
                    candidates.append(corpus[doc_id]["text"])
                    doc_ids.append(doc_id)

            if not candidates:
                reranked[qid] = {}
                continue

            ranked = rerank_documents(query_text, candidates)

            reranked[qid] = {}
            for item in ranked[:top_k]:
                idx = item["index"]
                reranked[qid][doc_ids[idx]] = float(item["relevance_score"])

        return reranked
