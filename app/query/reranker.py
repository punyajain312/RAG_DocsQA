"""Cross-encoder reranker: rescore (query, chunk) pairs and take top-N."""

import logging

from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

_RERANKER: CrossEncoder | None = None
_RERANKER_NAME: str = ""


def get_reranker(model_name: str) -> CrossEncoder:
    global _RERANKER, _RERANKER_NAME
    if _RERANKER is None or _RERANKER_NAME != model_name:
        logger.info("Loading reranker model '%s'", model_name)
        _RERANKER = CrossEncoder(model_name)
        _RERANKER_NAME = model_name
    return _RERANKER


def rerank(
    query: str,
    chunks: list[dict],
    model_name: str,
    top_n: int = 5,
) -> list[dict]:
    """Score each (query, chunk_text) pair, return top-n sorted by score."""
    if not chunks:
        return []

    reranker = get_reranker(model_name)
    pairs = [(query, chunk["text"]) for chunk in chunks]
    scores = reranker.predict(pairs)

    scored = sorted(
        zip(scores, chunks), key=lambda x: x[0], reverse=True
    )
    top = [chunk for _, chunk in scored[:top_n]]
    logger.info(
        "Reranked %d chunks -> kept top %d (best score=%.3f)",
        len(chunks),
        len(top),
        float(scored[0][0]) if scored else 0.0,
    )
    return top
