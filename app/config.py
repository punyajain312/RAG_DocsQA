"""Central configuration via pydantic-settings; all secrets loaded from .env."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-sonnet-4-6", env="ANTHROPIC_MODEL")

    # Ollama fallback
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.2", env="OLLAMA_MODEL")

    # LLM provider: "anthropic" or "ollama"
    llm_provider: str = Field(default="anthropic", env="LLM_PROVIDER")

    # Qdrant — set QDRANT_URL for cloud (e.g. Qdrant Cloud), otherwise host:port for local
    qdrant_host: str = Field(default="localhost", env="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, env="QDRANT_PORT")
    qdrant_url: str = Field(default="", env="QDRANT_URL")
    qdrant_api_key: str = Field(default="", env="QDRANT_API_KEY")
    qdrant_collection: str = Field(default="docqa", env="QDRANT_COLLECTION")

    # Embedding model
    embedding_model: str = Field(
        default="BAAI/bge-small-en-v1.5", env="EMBEDDING_MODEL"
    )
    embedding_dim: int = Field(default=384, env="EMBEDDING_DIM")

    # Reranker
    reranker_model: str = Field(
        default="BAAI/bge-reranker-base", env="RERANKER_MODEL"
    )
    use_reranker: bool = Field(default=True, env="USE_RERANKER")

    # Retrieval
    retrieval_top_k: int = Field(default=20, env="RETRIEVAL_TOP_K")
    rerank_top_n: int = Field(default=5, env="RERANK_TOP_N")

    # Chunking
    chunk_tokens: int = Field(default=500, env="CHUNK_TOKENS")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
