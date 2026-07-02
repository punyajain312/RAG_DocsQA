"""FastAPI application: /ingest, /query, /health endpoints."""

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.config import settings
from app.ingestion.chunker import chunk_pages
from app.ingestion.embedder import embed_texts
from app.ingestion.parser import parse_pdf_bytes
from app.llm.anthropic_client import AnthropicClient
from app.llm.base import LLMClient
from app.llm.groq_client import GroqClient
from app.llm.ollama_client import OllamaClient
from app.models import HealthResponse, IngestResponse, QueryRequest, QueryResponse
from app.query.pipeline import run_query
from app.store.qdrant_store import ensure_collection, get_client, is_healthy, upsert_chunks

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

_llm_client: LLMClient | None = None


def _get_llm() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        if settings.llm_provider == "groq":
            if not settings.groq_api_key:
                raise RuntimeError("GROQ_API_KEY is not set (get one free at console.groq.com)")
            _llm_client = GroqClient(settings.groq_api_key, settings.groq_model)
        elif settings.llm_provider == "ollama":
            _llm_client = OllamaClient(settings.ollama_base_url, settings.ollama_model)
        else:
            if not settings.anthropic_api_key:
                raise RuntimeError("ANTHROPIC_API_KEY is not set")
            _llm_client = AnthropicClient(settings.anthropic_api_key, settings.anthropic_model)
    return _llm_client


def _get_qdrant():
    return get_client(
        settings.qdrant_host, settings.qdrant_port,
        url=settings.qdrant_url, api_key=settings.qdrant_api_key,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    qdrant = _get_qdrant()
    ensure_collection(qdrant, settings.qdrant_collection, settings.embedding_dim)
    logger.info("Service started | provider=%s reranker=%s", settings.llm_provider, settings.use_reranker)
    yield


app = FastAPI(title="RAG DocQA", version="1.0.0", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
async def health():
    qdrant = _get_qdrant()
    return HealthResponse(
        status="ok",
        qdrant="ok" if is_healthy(qdrant) else "unavailable",
        llm_provider=settings.llm_provider,
    )


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        pages = parse_pdf_bytes(content, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    chunks = chunk_pages(pages, settings.chunk_tokens, settings.chunk_overlap)
    if not chunks:
        raise HTTPException(status_code=422, detail="No text could be extracted from the PDF")

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts, settings.embedding_model)

    qdrant = _get_qdrant()
    count = upsert_chunks(qdrant, settings.qdrant_collection, chunks, vectors)

    document_id = str(uuid.uuid4())
    logger.info("Ingested '%s' -> %d chunks | doc_id=%s", file.filename, count, document_id)
    return IngestResponse(document_id=document_id, chunks_indexed=count, filename=file.filename)


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    try:
        result = run_query(req.question, _get_llm(), top_k=req.top_k)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return result
