# INFRASTRUCTURE

RRF_K = 60
CC_ALPHA = 0.8


# FUNCTIONS

# Fuse two ranked result lists using Reciprocal Rank Fusion
def rrf_fusion(vector_results: list[dict], keyword_results: list[dict], top_k: int) -> list[dict]:
    scores = {}
    chunks = {}

    for rank, r in enumerate(vector_results, start=1):
        key = (r['collection'], r['document'], r['chunk_index'])
        scores[key] = scores.get(key, 0.0) + 1.0 / (RRF_K + rank)
        chunks[key] = r

    for rank, r in enumerate(keyword_results, start=1):
        key = (r['collection'], r['document'], r['chunk_index'])
        scores[key] = scores.get(key, 0.0) + 1.0 / (RRF_K + rank)
        if key not in chunks:
            chunks[key] = r

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [{**chunks[key], 'score': round(score, 6)} for key, score in ranked]


# Fuse two ranked result lists using Convex Combination with min-max normalization
def cc_fusion(vector_results: list[dict], keyword_results: list[dict], top_k: int, alpha: float = CC_ALPHA) -> list[dict]:
    max_vec = max((r['score'] for r in vector_results), default=0.0)
    max_kw = max((r['score'] for r in keyword_results), default=0.0)

    scores = {}
    chunks = {}

    if max_vec > 0:
        for r in vector_results:
            key = (r['collection'], r['document'], r['chunk_index'])
            scores[key] = alpha * (r['score'] / max_vec)
            chunks[key] = r

    if max_kw > 0:
        for r in keyword_results:
            key = (r['collection'], r['document'], r['chunk_index'])
            sparse_contrib = (1 - alpha) * (r['score'] / max_kw)
            scores[key] = scores.get(key, 0.0) + sparse_contrib
            if key not in chunks:
                chunks[key] = r

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [{**chunks[key], 'score': round(score, 6)} for key, score in ranked]
