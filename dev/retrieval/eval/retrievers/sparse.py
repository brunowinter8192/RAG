import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
from src.rag.sparse_embedder import sparse_embed_workflow

from .base import BaseRetriever


class SparseRetriever(BaseRetriever):
    """Sparse SPLADE retriever using sparse cosine similarity."""

    def __init__(self, model: str | None = None, collection: str | None = None):
        self.model = model
        self.collection = collection

    def name(self) -> str:
        return "Sparse(splade++)"

    def search(self, corpus: dict, queries: dict, top_k: int) -> dict[str, dict[str, float]]:
        corpus_ids = list(corpus.keys())
        query_ids = list(queries.keys())
        query_texts = [queries[qid] for qid in query_ids]

        if self.collection:
            corpus_dicts, corpus_ids = _load_sparse_from_db(self.collection, corpus_ids)
        else:
            corpus_texts = [corpus[cid]["text"] for cid in corpus_ids]
            corpus_vecs = _batched_sparse_embed(corpus_texts)
            corpus_dicts = [_to_dict(v) for v in corpus_vecs]

        corpus_norms = np.array([_l2_norm(d) for d in corpus_dicts])
        query_vecs = sparse_embed_workflow(query_texts)

        results = {}
        for i, qid in enumerate(query_ids):
            query_dict = _to_dict(query_vecs[i])
            query_norm = _l2_norm(query_dict)

            scores = []
            for j, doc_dict in enumerate(corpus_dicts):
                dot = sum(query_dict[idx] * doc_dict[idx] for idx in query_dict if idx in doc_dict)
                denom = query_norm * corpus_norms[j]
                scores.append(dot / denom if denom > 0 else 0.0)

            scores_arr = np.array(scores)
            top_indices = np.argsort(scores_arr)[::-1][:top_k]
            results[qid] = {corpus_ids[idx]: float(scores_arr[idx]) for idx in top_indices}

        return results


# Batch sparse embedding to avoid timeout on large corpus
def _batched_sparse_embed(texts: list[str], batch_size: int = 32) -> list[dict]:
    all_vecs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        all_vecs.extend(sparse_embed_workflow(batch))
        if len(texts) > batch_size:
            print(f"  Sparse embedded {min(i + batch_size, len(texts))}/{len(texts)}", end="\r")
    if len(texts) > batch_size:
        print()
    return all_vecs


# Load sparse embeddings from DB, return (list_of_dicts, ordered_corpus_ids) matching corpus keys
def _load_sparse_from_db(collection: str, corpus_ids: list[str]) -> tuple[list[dict], list[str]]:
    from src.rag.retriever import get_connection
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT sparse_embedding, document, chunk_index FROM documents WHERE collection = %s ORDER BY document, chunk_index",
        (collection,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    corpus_id_set = set(corpus_ids)
    ordered_ids = []
    sparse_dicts = []
    for sparse_embedding, document, chunk_index in rows:
        key = f"chunk_{chunk_index}_{document}"
        if key in corpus_id_set:
            ordered_ids.append(key)
            sparse_dicts.append({int(i): float(v) for i, v in zip(sparse_embedding.indices(), sparse_embedding.values())})

    return sparse_dicts, ordered_ids


# Convert sparse vector dict {indices, values} to index→value dict
def _to_dict(sparse: dict) -> dict:
    return {int(idx): float(val) for idx, val in zip(sparse["indices"], sparse["values"])}


# L2 norm of a sparse dict
def _l2_norm(d: dict) -> float:
    return sum(v * v for v in d.values()) ** 0.5
