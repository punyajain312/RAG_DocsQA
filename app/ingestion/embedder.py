"""Chunk text -> dense vectors via sentence-transformers."""

import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_MODEL: SentenceTransformer | None = None
_MODEL_NAME: str = ""


def get_model(model_name: str) -> SentenceTransformer:
    global _MODEL, _MODEL_NAME
    if _MODEL is None or _MODEL_NAME != model_name:
        logger.info("Loading embedding model '%s'", model_name)
        _MODEL = SentenceTransformer(model_name)
        _MODEL_NAME = model_name
    return _MODEL


def embed_texts(texts: list[str], model_name: str, batch_size: int = 64) -> list[list[float]]:
    """Return a list of float vectors, one per input text."""
    if not texts:
        return []
    model = get_model(model_name)
    # BGE models perform better with the query prefix on queries, but for
    # indexing we embed the raw text.
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=len(texts) > 100,
    )
    return [v.tolist() for v in vectors]


def embed_query(query: str, model_name: str) -> list[float]:
    """Embed a single query; BGE expects an instruction prefix for retrieval."""
    model = get_model(model_name)
    prefixed = f"Represent this sentence for searching relevant passages: {query}"
    vector = model.encode(
        prefixed,
        normalize_embeddings=True,
    )
    return vector.tolist()
