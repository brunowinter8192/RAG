from .base import BaseRetriever
from .dense import DenseRetriever
from .sparse import SparseRetriever


class HybridRetriever(BaseRetriever):
    """Hybrid retriever fusing Dense and Sparse results with Reciprocal Rank Fusion."""

    def __init__(self, dense: DenseRetriever, sparse: SparseRetriever, rrf_k: int = 60):
        self.dense = dense
        self.sparse = sparse
        self.rrf_k = rrf_k

    def name(self) -> str:
        dims = self.dense.truncate_dims or "full"
        return f"Hybrid(rrf_k={self.rrf_k}, {dims}d)"

    def search(self, corpus: dict, queries: dict, top_k: int) -> dict[str, dict[str, float]]:
        dense_results = self.dense.search(corpus, queries, top_k)
        sparse_results = self.sparse.search(corpus, queries, top_k)
        return _rrf_fusion(dense_results, sparse_results, top_k, self.rrf_k)


# Fuse two eval-format result dicts {query_id: {doc_id: score}} using RRF
def _rrf_fusion(results_a: dict, results_b: dict, top_k: int, rrf_k: int) -> dict:
    fused = {}
    for qid in set(results_a) | set(results_b):
        scores = {}

        for rank, (doc_id, _) in enumerate(
            sorted(results_a.get(qid, {}).items(), key=lambda x: x[1], reverse=True), start=1
        ):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (rrf_k + rank)

        for rank, (doc_id, _) in enumerate(
            sorted(results_b.get(qid, {}).items(), key=lambda x: x[1], reverse=True), start=1
        ):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (rrf_k + rank)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        fused[qid] = dict(ranked)

    return fused
