K_VALUES = [3, 5, 10]

METRICS = {
    "ndcg_cut." + ",".join(str(k) for k in K_VALUES),
    "recall." + ",".join(str(k) for k in K_VALUES),
    "P." + ",".join(str(k) for k in K_VALUES),
}

DATASETS_DIR = "dev/retrieval_eval/datasets"
RESULTS_DIR = "dev/retrieval_eval/results"
