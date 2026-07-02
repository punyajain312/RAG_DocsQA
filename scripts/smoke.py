"""Quick end-to-end smoke test: ingest one PDF, answer one question."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings
from app.ingestion.chunker import chunk_pages
from app.ingestion.embedder import embed_query, embed_texts
from app.ingestion.parser import parse_pdf
from app.llm.anthropic_client import AnthropicClient
from app.query.pipeline import SYSTEM_PROMPT, _build_user_prompt
from app.store.qdrant_store import ensure_collection, get_client, search, upsert_chunks

PDF_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/sample.pdf"
QUESTION = sys.argv[2] if len(sys.argv) > 2 else "What is the main topic of this document?"


def main():
    print(f"[smoke] Parsing {PDF_PATH}")
    pages = parse_pdf(PDF_PATH)
    print(f"[smoke] {len(pages)} pages parsed")

    chunks = chunk_pages(pages, settings.chunk_tokens, settings.chunk_overlap)
    print(f"[smoke] {len(chunks)} chunks created")

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts, settings.embedding_model)
    print(f"[smoke] {len(vectors)} vectors computed")

    client = get_client(settings.qdrant_host, settings.qdrant_port)
    ensure_collection(client, settings.qdrant_collection, settings.embedding_dim)
    upsert_chunks(client, settings.qdrant_collection, chunks, vectors)
    print("[smoke] Upserted to Qdrant")

    q_vec = embed_query(QUESTION, settings.embedding_model)
    hits = search(client, settings.qdrant_collection, q_vec, top_k=5)
    print(f"[smoke] Retrieved {len(hits)} chunks")

    llm = AnthropicClient(settings.anthropic_api_key, settings.anthropic_model)
    user_prompt = _build_user_prompt(QUESTION, hits)
    answer = llm.complete(SYSTEM_PROMPT, user_prompt)

    print("\n" + "=" * 60)
    print(f"Q: {QUESTION}")
    print(f"A: {answer}")
    print("=" * 60)


if __name__ == "__main__":
    main()
