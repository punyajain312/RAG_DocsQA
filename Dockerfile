FROM python:3.11-slim

WORKDIR /app

# Install system deps for PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only torch — the default PyPI wheel now includes CUDA on both amd64 and arm64,
# which is unnecessary for this server and adds 2-3 GB. Try the CPU-only index first (much smaller),
# fall back to default PyPI if the CPU index has no wheel for this platform.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    || pip install --no-cache-dir torch

RUN pip install --no-cache-dir -r requirements.txt

# Pre-download models so the container starts without internet at runtime
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('BAAI/bge-reranker-base')"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
