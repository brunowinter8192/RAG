# INFRASTRUCTURE

BASELINE = {
    "mode": "cc",
    "top_k": 12,
    "alpha": 0.8,
    "rrf_k": 60,
    "score_threshold": 0.0,
    "query_prefix": True,
}

SWEEP_RANGES = {
    "mode":            ["dense", "sparse", "hybrid", "cc", "cc+rerank", "hybrid+rerank", "bm25"],
    "top_k":           [5, 10, 20],
    "alpha":           [0.5, 0.6, 0.7, 0.8, 0.9],
    "rrf_k":           [30, 60, 90],
    "score_threshold": [0.0, 0.3, 0.5],
    "query_prefix":    [True, False],
}
