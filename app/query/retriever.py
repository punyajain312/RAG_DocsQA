"""Top-K vector search over the Qdrant collection."""

import logging

from qdrant_client import QdrantClient

from app.store.qdrant_store import search

logger = logging.getLogger(__name__)


def retrieve(
    client: QdrantClient,
    collection_name: str,
    query_vector: list[float],
    top_k: int = 20,
) -> list[dict]:
    """Retrieve top-k chunks by cosine similarity."""
    hits = search(client, collection_name, query_vector, top_k=top_k)
    logger.info("Retrieved %d chunks for query", len(hits))
    return hits
