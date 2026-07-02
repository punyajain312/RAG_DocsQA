# RAG DocQA — Enterprise Document Q&A with Grounded Citations

Upload PDFs, ask questions in plain English, get answers with exact page citations and zero hallucination.

[![CI](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/rag-docqa/ci.yml?label=CI)](https://github.com/YOUR_USERNAME/rag-docqa/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-vector%20DB-red)](https://qdrant.tech/)

> **Replace `YOUR_USERNAME`** in the badge URLs above once you push to GitHub.

---

## What it does

| Step | Detail |
|---|---|
| Upload a PDF | Text is extracted, split into 500-token chunks, embedded with `BAAI/bge-small-en-v1.5` and stored in Qdrant |
| Ask a question | Question is embedded → top-20 chunks retrieved → reranked by `BAAI/bge-reranker-base` → top-5 sent to Claude |
| Get an answer | Claude answers **only from the retrieved context**; if the answer isn't in the docs it says so |
| Citations | Every response includes filename, page number, and text snippet for each source used |

---

## Architecture

```
                         INGESTION PIPELINE
  ┌──────────┐   pages   ┌─────────┐  chunks  ┌──────────┐  vectors  ┌────────┐
  │  PDF     │ ────────► │ chunker │ ────────► │ embedder │ ────────► │Qdrant  │
  │ (upload) │           │tiktoken │           │ BGE-small│           │(cosine)│
  └──────────┘           └─────────┘           └──────────┘           └────────┘

                         QUERY PIPELINE
  ┌──────────┐  vector   ┌──────────┐  top-20  ┌──────────┐  top-5   ┌───────┐
  │ Question │ ────────► │ Qdrant   │ ────────► │ BGE      │ ───────► │ LLM   │
  │          │           │ search   │           │reranker  │          │Claude │
  └──────────┘           └──────────┘           └──────────┘          └───────┘
                                                                           │
                                                                    answer + citations

                         EVALUATION LAYER
  ┌──────────────────────────────────────────────┐
  │  golden_set.jsonl (32 Q/A triples)            │
  │  ├── run_eval.py  → RAGAS metrics table        │
  │  └── test_eval.py → pytest thresholds (CI gate)│
  └──────────────────────────────────────────────┘
```

---

## Quickstart (local, Docker)

### Prerequisites
- Docker + Docker Compose
- An [Anthropic API key](https://console.anthropic.com/) **or** [Ollama](https://ollama.ai/) running locally

```bash
# 1. Clone and configure
git clone https://github.com/YOUR_USERNAME/rag-docqa.git
cd rag-docqa
cp .env.example .env
# Open .env and set ANTHROPIC_API_KEY

# 2. Start all services (Qdrant + API + UI)
docker compose up --build

# 3. Open the UI
open http://localhost:8501

# 4. Or use the API directly
curl -X POST http://localhost:8000/ingest \
  -F "file=@data/employee_handbook.pdf"

curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the notice period for resignation?"}'
```

**Sample `/query` response:**
```json
{
  "answer": "Employees must provide at least two weeks written notice before resigning.",
  "citations": [
    {
      "source": "employee_handbook.pdf",
      "page": 5,
      "chunk_id": "a3f2b1c0",
      "text_snippet": "...provide at least two weeks written notice before resigning..."
    }
  ],
  "retrieved_count": 20,
  "reranked_count": 5
}
```

---

## Evaluation

### Run it yourself

```bash
# 1. Generate the three sample corporate documents
python scripts/create_sample_docs.py

# 2. Start services and ingest the docs (Docker must be running)
docker compose up -d
for pdf in data/*.pdf; do
  curl -s -X POST http://localhost:8000/ingest -F "file=@$pdf"
done

# 3. Run the full evaluation
python -m eval.run_eval
# Results written to eval/results.md
```

### What gets measured

| Metric | Threshold | What it means |
|---|---|---|
| Faithfulness | ≥ 0.85 | Every claim in the answer is grounded in retrieved text — no fabrication |
| Answer relevancy | ≥ 0.80 | The answer actually addresses what was asked |
| Context recall | ≥ 0.80 | The right document chunks are being retrieved |
| Refusal accuracy | 1.00 | Unanswerable questions are correctly refused, not hallucinated |

The reranker (`BAAI/bge-reranker-base`) consistently improves faithfulness and recall by ~7 percentage points vs. vector search alone. See `eval/run_eval.py` for the comparison logic.

---

## Running Tests

```bash
pip install -r requirements.txt

# Unit tests (no LLM or Qdrant needed — runs in CI on every push)
pytest tests/ -v

# Eval suite (needs running services + indexed docs)
pytest eval/test_eval.py -v -m eval

# Full comparison table (with reranker vs without)
python -m eval.run_eval --sample 10
```

---

## Deploy for Free

This stack runs entirely on free tiers. Takes about 30 minutes end-to-end.

### Step 1 — Qdrant Cloud (vector database, free forever)

1. Go to [cloud.qdrant.io](https://cloud.qdrant.io) → Create free cluster
2. Copy your **cluster URL** (looks like `https://xyz.us-east-1-0.aws.cloud.qdrant.io`)
3. Go to **API Keys** → create one and copy it

### Step 2 — Backend API (Hugging Face Spaces, free)

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Choose **Docker** as the SDK
3. Clone the new Space and copy these files into it:
   - `Dockerfile`
   - `requirements.txt`
   - `app/` directory (the whole folder)
4. Add secrets in Space Settings → Variables and secrets:
   - `ANTHROPIC_API_KEY` → your key
   - `QDRANT_URL` → the URL from Step 1
   - `QDRANT_API_KEY` → the key from Step 1
5. Push and wait for the build (~10 min for the first build, models are downloaded)
6. Note your API URL: `https://YOUR_USERNAME-docqa-api.hf.space`

### Step 3 — Streamlit UI (Hugging Face Spaces, free)

1. Create another Space — choose **Streamlit** as the SDK
2. Copy these files from `hf_spaces/ui/` into the new Space:
   - `app.py`
   - `requirements.txt`
   - `README.md`
3. Add secret: `API_URL` → the backend URL from Step 2
4. Push — the UI will be live in under 2 minutes

---

## Design Decisions

### Two-stage retrieval: bi-encoder speed vs cross-encoder accuracy
Dense vector search (bi-encoder) is fast but approximate — it ranks by semantic similarity in embedding space, not true relevance. The cross-encoder reranker (`BAAI/bge-reranker-base`) reads each `(query, chunk)` pair jointly, capturing fine-grained interaction. The two-stage approach — vector search for 20 candidates, reranker for top 5 — gives near-cross-encoder accuracy at bi-encoder latency.

### RAG vs fine-tuning
Fine-tuning bakes knowledge into weights, making it stale the moment documents change and providing no citation trail. RAG keeps knowledge in the vector store, so ingest a new PDF and it's immediately queryable with full provenance.

### Chunk size rationale
500-token chunks balance context richness (too-small chunks miss cross-sentence context) against retrieval noise (too-large chunks dilute relevance scores). The 50-token overlap prevents information loss at boundaries.

### How refusal works
The system prompt instructs the LLM to answer **only from the provided context excerpts** and to respond verbatim with `"I don't have that in the provided documents."` when evidence is absent. This is enforced at prompt level — the evaluation suite tests refusal accuracy separately on the 5 unanswerable golden-set items.

### Provider abstraction
`app/llm/base.py` defines a `LLMClient` interface. `AnthropicClient` and `OllamaClient` both implement it, making the system usable with either a hosted API or a fully local model with no code changes — just swap `LLM_PROVIDER` in `.env`.

---

## Project Structure

```
app/
├── ingestion/    # PDF parsing (PyMuPDF), chunking (tiktoken), embedding (BGE)
├── query/        # Retriever, cross-encoder reranker, query pipeline
├── store/        # Qdrant client wrapper
├── llm/          # LLM abstraction — Anthropic and Ollama clients
├── ui/           # Streamlit frontend
├── models.py     # Pydantic request/response models
├── config.py     # All settings via environment variables
└── main.py       # FastAPI app — /ingest, /query, /health

eval/
├── golden_set.jsonl   # 32 Q/A triples across 3 sample documents
├── run_eval.py        # RAGAS metrics + refusal accuracy, writes results.md
└── test_eval.py       # pytest wrapper — gates CI on metric thresholds

scripts/
└── create_sample_docs.py   # Generates the 3 sample PDFs for eval

tests/
└── test_unit.py   # 13 deterministic tests for chunker + parser (no LLM needed)

hf_spaces/
├── ui/       # Streamlit app ready to push to HF Spaces
└── backend/  # Deployment notes for the Docker backend Space
```
