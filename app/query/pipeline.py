"""Orchestrates retrieve -> rerank -> prompt -> LLM for a single query."""

import logging
import time

from app.config import settings
from app.ingestion.embedder import embed_query
from app.llm.base import LLMClient
from app.models import Citation, QueryResponse
from app.query.reranker import rerank
from app.query.retriever import retrieve
from app.store.qdrant_store import get_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a precise document assistant. Answer questions using ONLY the document excerpts provided below.

Rules:
1. Ground every claim in the provided context. Do not use outside knowledge.
2. If the context does not contain sufficient information to answer the question, respond with exactly: "I don't have that in the provided documents."
3. After your answer, list the sources you used in the format: [Source: <filename>, Page <page>].
4. Be concise and factual."""


def _build_user_prompt(question: str, chunks: list[dict]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Excerpt {i} | {chunk['source_filename']}, Page {chunk['page_number']}]\n{chunk['text']}"
        )
    context = "\n\n---\n\n".join(context_parts)
    return f"Context:\n{context}\n\nQuestion: {question}"


def run_query(
    question: str,
    llm_client: LLMClient,
    top_k: int | None = None,
) -> QueryResponse:
    """End-to-end query: embed -> retrieve -> rerank -> generate."""
    t0 = time.time()
    effective_top_k = top_k or settings.retrieval_top_k

    # Embed the query
    query_vector = embed_query(question, settings.embedding_model)

    # Retrieve
    qdrant_client = get_client(
        settings.qdrant_host, settings.qdrant_port,
        url=settings.qdrant_url, api_key=settings.qdrant_api_key,
    )
    hits = retrieve(
        qdrant_client,
        settings.qdrant_collection,
        query_vector,
        top_k=effective_top_k,
    )
    retrieved_count = len(hits)

    # Rerank
    if settings.use_reranker and hits:
        final_chunks = rerank(
            question,
            hits,
            settings.reranker_model,
            top_n=settings.rerank_top_n,
        )
    else:
        final_chunks = hits[: settings.rerank_top_n]

    reranked_count = len(final_chunks)

    # Generate
    user_prompt = _build_user_prompt(question, final_chunks)
    answer = llm_client.complete(SYSTEM_PROMPT, user_prompt)

    # Build citations from chunks that were actually used
    citations = [
        Citation(
            source=c["source_filename"],
            page=c["page_number"],
            chunk_id=c["chunk_id"],
            text_snippet=c["text"][:200].replace("\n", " "),
        )
        for c in final_chunks
    ]

    elapsed = time.time() - t0
    logger.info(
        "Query done in %.2fs | retrieved=%d reranked=%d",
        elapsed, retrieved_count, reranked_count,
    )

    return QueryResponse(
        answer=answer,
        citations=citations,
        retrieved_count=retrieved_count,
        reranked_count=reranked_count,
    )
