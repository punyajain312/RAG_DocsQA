"""Pydantic request/response schemas for the API."""


from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    document_id: str
    chunks_indexed: int
    filename: str


class Citation(BaseModel):
    source: str
    page: int
    chunk_id: str
    text_snippet: str


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=100)


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieved_count: int
    reranked_count: int


class HealthResponse(BaseModel):
    status: str
    qdrant: str
    llm_provider: str


class ChunkMetadata(BaseModel):
    source_filename: str
    page_number: int
    chunk_id: str
    text: str
