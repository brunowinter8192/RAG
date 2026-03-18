import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
from src.rag.embedder import embed_workflow

from .base import BaseRetriever


class DenseRetriever(BaseRetriever):
    """Dense retriever with optional MRL dimension truncation."""

    def __init__(self, truncate_dims: int | None = None, query_prefix: str | None = None, collection: str | None = None):
        self.truncate_dims = truncate_dims
        self.query_prefix = query_prefix or "Instruct: Given a search query, retrieve relevant passages that answer the query\nQuery: "
        self.collection = collection

    def name(self) -> str:
        dims = self.truncate_dims or "full"
        return f"Dense({dims}d)"

    def search(self, corpus: dict, queries: dict, top_k: int) -> dict[str, dict[str, float]]:
        corpus_ids = list(corpus.keys())
        query_ids = list(queries.keys())
        query_texts = [queries[qid] for qid in query_ids]

        if self.collection:
            corpus_embeddings, corpus_ids = _load_dense_from_db(self.collection, corpus_ids, self.truncate_dims)
        else:
            corpus_texts = [corpus[cid]["text"] for cid in corpus_ids]
            corpus_embeddings = self._embed_and_truncate(corpus_texts)

        query_embeddings = self._embed_and_truncate(query_texts, is_query=True)

        results = {}
        for i, qid in enumerate(query_ids):
            scores = cosine_similarities(query_embeddings[i], corpus_embeddings)
            top_indices = np.argsort(scores)[::-1][:top_k]
            results[qid] = {corpus_ids[idx]: float(scores[idx]) for idx in top_indices}

        return results

    def _embed_and_truncate(self, texts: list[str], is_query: bool = False, batch_size: int = 32) -> np.ndarray:
        prefix = self.query_prefix if is_query else None
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            all_embeddings.extend(embed_workflow(batch, prefix=prefix))
            if len(texts) > batch_size:
                print(f"  Embedded {min(i + batch_size, len(texts))}/{len(texts)}", end="\r")
        if len(texts) > batch_size:
            print()
        arr = np.array(all_embeddings)

        if self.truncate_dims and self.truncate_dims < arr.shape[1]:
            arr = arr[:, :self.truncate_dims]
            norms = np.linalg.norm(arr, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1, norms)
            arr = arr / norms

        return arr


# Load dense embeddings from DB, return (array, ordered_corpus_ids) matching corpus keys
def _load_dense_from_db(collection: str, corpus_ids: list[str], truncate_dims: int | None) -> tuple[np.ndarray, list[str]]:
    from src.rag.retriever import get_connection
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT embedding, document, chunk_index FROM documents WHERE collection = %s ORDER BY document, chunk_index",
        (collection,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    corpus_id_set = set(corpus_ids)
    ordered_ids = []
    embeddings = []
    for embedding, document, chunk_index in rows:
        key = f"chunk_{chunk_index}_{document}"
        if key in corpus_id_set:
            ordered_ids.append(key)
            embeddings.append(np.array(embedding, dtype=np.float32))

    arr = np.stack(embeddings)
    if truncate_dims and truncate_dims < arr.shape[1]:
        arr = arr[:, :truncate_dims]
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        arr = arr / norms

    return arr, ordered_ids


# Cosine similarity between a single query vector and matrix of corpus vectors
def cosine_similarities(query: np.ndarray, corpus: np.ndarray) -> np.ndarray:
    query_norm = query / (np.linalg.norm(query) or 1)
    corpus_norms = corpus / (np.linalg.norm(corpus, axis=1, keepdims=True) + 1e-10)
    return corpus_norms @ query_norm
