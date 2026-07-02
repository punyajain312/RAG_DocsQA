"""Ingest all PDFs in data/ directly into Qdrant — no API server required.

Usage:
    python scripts/ingest_docs.py
    QDRANT_HOST=localhost python scripts/ingest_docs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.ingestion.chunker import chunk_pages
from app.ingestion.embedder import embed_texts
from app.ingestion.parser import parse_pdf_bytes
from app.store.qdrant_store import ensure_collection, get_client, upsert_chunks


def main() -> None:
    data_dir = Path("data")
    pdfs = list(data_dir.glob("*.pdf"))
    if not pdfs:
        print("No PDFs in data/. Run 'python scripts/create_sample_docs.py' first.")
        sys.exit(1)

    qdrant = get_client(
        settings.qdrant_host,
        settings.qdrant_port,
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )
    ensure_collection(qdrant, settings.qdrant_collection, settings.embedding_dim)

    for pdf_path in sorted(pdfs):
        content = pdf_path.read_bytes()
        pages = parse_pdf_bytes(content, pdf_path.name)
        chunks = chunk_pages(pages, settings.chunk_tokens, settings.chunk_overlap)
        vectors = embed_texts([c["text"] for c in chunks], settings.embedding_model)
        count = upsert_chunks(qdrant, settings.qdrant_collection, chunks, vectors)
        print(f"  {pdf_path.name} -> {count} chunks")

    print(f"Done. Ingested {len(pdfs)} document(s).")


if __name__ == "__main__":
    main()
