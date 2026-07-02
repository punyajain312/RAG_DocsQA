"""Qdrant collection management: upsert chunks, vector search."""

import logging
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse

logger = logging.getLogger(__name__)

_CLIENT: QdrantClient | None = None


def get_client(host: str, port: int, url: str = "", api_key: str = "") -> QdrantClient:
    global _CLIENT
    if _CLIENT is None:
        if url:
            _CLIENT = QdrantClient(url=url, api_key=api_key or None)
            logger.info("Connected to Qdrant Cloud at %s", url)
        else:
            _CLIENT = QdrantClient(host=host, port=port)
            logger.info("Connected to Qdrant at %s:%d", host, port)
    return _CLIENT


def ensure_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int,
) -> None:
    """Create collection if it does not exist."""
    try:
        client.get_collection(collection_name)
        logger.debug("Collection '%s' already exists", collection_name)
    except (UnexpectedResponse, Exception):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=qdrant_models.VectorParams(
                size=vector_size,
                distance=qdrant_models.Distance.COSINE,
            ),
        )
        logger.info("Created collection '%s' (dim=%d)", collection_name, vector_size)


def upsert_chunks(
    client: QdrantClient,
    collection_name: str,
    chunks: list[dict],
    vectors: list[list[float]],
) -> int:
    """Upsert chunk vectors with metadata payload. Returns number of points upserted."""
    if not chunks:
        return 0

    points = []
    for chunk, vector in zip(chunks, vectors):
        point_id = str(uuid.uuid4())
        points.append(
            qdrant_models.PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "chunk_id": chunk["chunk_id"],
                    "source_filename": chunk["source_filename"],
                    "page_number": chunk["page_number"],
                    "text": chunk["text"],
                    "token_count": chunk.get("token_count", 0),
                },
            )
        )

    client.upsert(collection_name=collection_name, points=points)
    logger.info("Upserted %d points into '%s'", len(points), collection_name)
    return len(points)


def search(
    client: QdrantClient,
    collection_name: str,
    query_vector: list[float],
    top_k: int = 20,
) -> list[dict]:
    """Return top-k results as list of payload dicts with score."""
    # qdrant-client >= 1.7 replaced .search() with .query_points()
    response = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )

    hits = []
    for r in response.points:
        payload = dict(r.payload)
        payload["score"] = r.score
        hits.append(payload)

    logger.debug("Vector search returned %d hits (top_k=%d)", len(hits), top_k)
    return hits


def is_healthy(client: QdrantClient) -> bool:
    try:
        client.get_collections()
        return True
    except Exception:
        return False
