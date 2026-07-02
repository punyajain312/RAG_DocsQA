"""Deterministic unit tests for chunker and parser — no LLM calls."""

import pytest

from app.ingestion.chunker import chunk_pages, chunk_text

# ---------------------------------------------------------------------------
# Chunker tests
# ---------------------------------------------------------------------------

SAMPLE_TEXT = " ".join([f"word{i}" for i in range(1000)])  # ~1000 tokens


def test_chunk_produces_output():
    chunks = chunk_text(SAMPLE_TEXT, "test.pdf", 1, chunk_tokens=500, overlap_tokens=50)
    assert len(chunks) >= 1


def test_chunk_metadata_fields():
    chunks = chunk_text(SAMPLE_TEXT, "doc.pdf", 3, chunk_tokens=200, overlap_tokens=20)
    for c in chunks:
        assert "text" in c
        assert "source_filename" in c
        assert "page_number" in c
        assert "chunk_id" in c
        assert c["source_filename"] == "doc.pdf"
        assert c["page_number"] == 3


def test_chunk_ids_are_unique():
    chunks = chunk_text(SAMPLE_TEXT, "doc.pdf", 1, chunk_tokens=200, overlap_tokens=20)
    ids = [c["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids)), "Chunk IDs must be unique"


def test_chunk_ids_are_deterministic():
    chunks1 = chunk_text(SAMPLE_TEXT, "doc.pdf", 1, chunk_tokens=200, overlap_tokens=20)
    chunks2 = chunk_text(SAMPLE_TEXT, "doc.pdf", 1, chunk_tokens=200, overlap_tokens=20)
    assert [c["chunk_id"] for c in chunks1] == [c["chunk_id"] for c in chunks2]


def test_chunk_token_count_within_limit():
    chunks = chunk_text(SAMPLE_TEXT, "doc.pdf", 1, chunk_tokens=500, overlap_tokens=50)
    for c in chunks:
        assert c["token_count"] <= 500


def test_empty_text_returns_empty():
    chunks = chunk_text("", "doc.pdf", 1)
    assert chunks == []


def test_whitespace_only_returns_empty():
    chunks = chunk_text("   \n\t  ", "doc.pdf", 1)
    assert chunks == []


def test_single_short_text_one_chunk():
    chunks = chunk_text("Hello world.", "doc.pdf", 1, chunk_tokens=500, overlap_tokens=50)
    assert len(chunks) == 1
    assert "Hello world" in chunks[0]["text"]


def test_overlap_creates_more_chunks_than_no_overlap():
    chunks_overlap = chunk_text(SAMPLE_TEXT, "doc.pdf", 1, chunk_tokens=200, overlap_tokens=50)
    chunks_no_overlap = chunk_text(SAMPLE_TEXT, "doc.pdf", 1, chunk_tokens=200, overlap_tokens=0)
    assert len(chunks_overlap) >= len(chunks_no_overlap)


def test_chunk_pages_aggregates_all_pages():
    pages = [
        {"text": SAMPLE_TEXT[:500], "source_filename": "doc.pdf", "page_number": 1},
        {"text": SAMPLE_TEXT[500:1000], "source_filename": "doc.pdf", "page_number": 2},
    ]
    chunks = chunk_pages(pages, chunk_tokens=200, overlap_tokens=20)
    sources = {c["page_number"] for c in chunks}
    assert 1 in sources
    assert 2 in sources


def test_chunk_pages_empty_input():
    chunks = chunk_pages([], chunk_tokens=200, overlap_tokens=20)
    assert chunks == []


# ---------------------------------------------------------------------------
# Parser tests (no PDF required — test input validation)
# ---------------------------------------------------------------------------

def test_parser_raises_on_missing_file():
    from app.ingestion.parser import parse_pdf
    with pytest.raises(FileNotFoundError):
        parse_pdf("/nonexistent/path/file.pdf")


def test_parser_raises_on_invalid_bytes():
    from app.ingestion.parser import parse_pdf_bytes
    with pytest.raises(ValueError):
        parse_pdf_bytes(b"not a pdf", "fake.pdf")


def test_parser_raises_on_empty_bytes():
    from app.ingestion.parser import parse_pdf_bytes
    with pytest.raises(ValueError):
        parse_pdf_bytes(b"", "empty.pdf")
