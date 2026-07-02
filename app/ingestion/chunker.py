"""Tokenizer-based text chunker with configurable size and overlap."""

import hashlib
import logging

import tiktoken

logger = logging.getLogger(__name__)

_ENC: tiktoken.Encoding | None = None


def _get_encoder() -> tiktoken.Encoding:
    global _ENC
    if _ENC is None:
        _ENC = tiktoken.get_encoding("cl100k_base")
    return _ENC


def _token_len(text: str) -> int:
    return len(_get_encoder().encode(text))


def chunk_text(
    text: str,
    source_filename: str,
    page_number: int,
    chunk_tokens: int = 500,
    overlap_tokens: int = 50,
) -> list[dict]:
    """Split text into overlapping token-bounded chunks with metadata."""
    enc = _get_encoder()
    token_ids = enc.encode(text)

    if not token_ids:
        return []

    chunks = []
    start = 0
    step = chunk_tokens - overlap_tokens

    while start < len(token_ids):
        end = min(start + chunk_tokens, len(token_ids))
        chunk_tokens_slice = token_ids[start:end]
        chunk_text_str = enc.decode(chunk_tokens_slice)

        if chunk_text_str.strip():
            chunk_id = hashlib.sha256(
                f"{source_filename}:{page_number}:{start}".encode()
            ).hexdigest()[:16]

            chunks.append(
                {
                    "text": chunk_text_str,
                    "source_filename": source_filename,
                    "page_number": page_number,
                    "chunk_id": chunk_id,
                    "token_count": len(chunk_tokens_slice),
                }
            )

        if end == len(token_ids):
            break
        start += step

    return chunks


def chunk_pages(
    pages: list[dict],
    chunk_tokens: int = 500,
    overlap_tokens: int = 50,
) -> list[dict]:
    """Chunk a list of parsed pages into overlapping chunks."""
    all_chunks = []
    for page in pages:
        page_chunks = chunk_text(
            text=page["text"],
            source_filename=page["source_filename"],
            page_number=page["page_number"],
            chunk_tokens=chunk_tokens,
            overlap_tokens=overlap_tokens,
        )
        all_chunks.extend(page_chunks)

    logger.info(
        "Chunked %d pages into %d chunks", len(pages), len(all_chunks)
    )
    return all_chunks
