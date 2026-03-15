import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.rag.embedder import embed_workflow

from .base import BaseRetriever


class DenseRetriever(BaseRetriever):
    """Dense retriever with optional MRL dimension truncation."""

    def __init__(self, truncate_dims: int | None = None, query_prefix: str | None = None):
        self.truncate_dims = truncate_dims
        self.query_prefix = query_prefix or "Instruct: Given a search query, retrieve relevant passages that answer the query\nQuery: "

    def name(self) -> str:
        dims = self.truncate_dims or "full"
        return f"Dense({dims}d)"

    def search(self, corpus: dict, queries: dict, top_k: int) -> dict[str, dict[str, float]]:
        corpus_ids = list(corpus.keys())
        corpus_texts = [corpus[cid]["text"] for cid in corpus_ids]
        query_ids = list(queries.keys())
        query_texts = [queries[qid] for qid in query_ids]

        corpus_embeddings = self._embed_and_truncate(corpus_texts)
        query_embeddings = self._embed_and_truncate(query_texts, is_query=True)

        results = {}
        for i, qid in enumerate(query_ids):
            scores = cosine_similarities(query_embeddings[i], corpus_embeddings)
            top_indices = np.argsort(scores)[::-1][:top_k]
            results[qid] = {corpus_ids[idx]: float(scores[idx]) for idx in top_indices}

        return results

    def _embed_and_truncate(self, texts: list[str], is_query: bool = False) -> np.ndarray:
        prefix = self.query_prefix if is_query else None
        embeddings = embed_workflow(texts, prefix=prefix)
        arr = np.array(embeddings)

        if self.truncate_dims and self.truncate_dims < arr.shape[1]:
            arr = arr[:, :self.truncate_dims]
            norms = np.linalg.norm(arr, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1, norms)
            arr = arr / norms

        return arr


# Cosine similarity between a single query vector and matrix of corpus vectors
def cosine_similarities(query: np.ndarray, corpus: np.ndarray) -> np.ndarray:
    query_norm = query / (np.linalg.norm(query) or 1)
    corpus_norms = corpus / (np.linalg.norm(corpus, axis=1, keepdims=True) + 1e-10)
    return corpus_norms @ query_norm
