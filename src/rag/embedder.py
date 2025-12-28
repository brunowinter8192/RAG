# INFRASTRUCTURE
import logging
from typing import Union
from sentence_transformers import SentenceTransformer

logging.basicConfig(
    filename='src/rag/logs/embedder.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

MODEL_NAME = "Alibaba-NLP/gte-Qwen2-7B-instruct"
MODEL_INSTANCE = None


# ORCHESTRATOR
def embed_workflow(texts: Union[str, list[str]], batch_size: int = 32) -> list[list[float]]:
    model = get_model()
    if isinstance(texts, str):
        texts = [texts]
    embeddings = generate_embeddings(model, texts, batch_size)
    logging.info(f"Embedded {len(texts)} texts")
    return embeddings


# FUNCTIONS

# Load or return cached model instance
def get_model() -> SentenceTransformer:
    global MODEL_INSTANCE
    if MODEL_INSTANCE is None:
        logging.info(f"Loading model: {MODEL_NAME}")
        MODEL_INSTANCE = SentenceTransformer(MODEL_NAME, trust_remote_code=True)
        logging.info("Model loaded successfully")
    return MODEL_INSTANCE


# Generate embeddings for list of texts
def generate_embeddings(model: SentenceTransformer, texts: list[str], batch_size: int) -> list[list[float]]:
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True
    )
    return embeddings.tolist()
