"""PDF -> raw text with page numbers using PyMuPDF."""

import logging
from pathlib import Path

import pymupdf

logger = logging.getLogger(__name__)


def parse_pdf(file_path: str | Path) -> list[dict]:
    """Return a list of {text, page_number, source_filename} dicts, one per page."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    pages = []
    try:
        doc = pymupdf.open(str(path))
    except Exception as exc:
        raise ValueError(f"Cannot open PDF '{path}': {exc}") from exc

    if doc.page_count == 0:
        raise ValueError(f"PDF '{path}' has no pages")

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if text.strip():
            pages.append(
                {
                    "text": text,
                    "page_number": page_num + 1,
                    "source_filename": path.name,
                }
            )

    doc.close()
    logger.info("Parsed %d pages from '%s'", len(pages), path.name)
    return pages


def parse_pdf_bytes(content: bytes, filename: str) -> list[dict]:
    """Parse a PDF from raw bytes (e.g., uploaded file)."""
    pages = []
    try:
        doc = pymupdf.open(stream=content, filetype="pdf")
    except Exception as exc:
        raise ValueError(f"Cannot parse PDF '{filename}': {exc}") from exc

    if doc.page_count == 0:
        raise ValueError(f"PDF '{filename}' has no pages")

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if text.strip():
            pages.append(
                {
                    "text": text,
                    "page_number": page_num + 1,
                    "source_filename": filename,
                }
            )

    doc.close()
    logger.info("Parsed %d pages from uploaded '%s'", len(pages), filename)
    return pages
