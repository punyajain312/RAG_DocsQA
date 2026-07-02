---
title: DocQA API
emoji: ⚡
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# DocQA FastAPI Backend

Docker-based Space running the RAG DocQA API (FastAPI + BGE embeddings + reranker).

## Required Secrets (set in Space Settings → Variables and secrets)

| Secret | Example |
|---|---|
| `ANTHROPIC_API_KEY` | `sk-ant-...` |
| `QDRANT_URL` | `https://abc123.us-east-1-0.aws.cloud.qdrant.io` |
| `QDRANT_API_KEY` | `your-qdrant-cloud-api-key` |

## Deployment steps

1. Create a new **Docker** Space on huggingface.co/spaces
2. Clone this repo's `hf_spaces/backend/` contents into that Space
3. Copy the root `Dockerfile`, `requirements.txt`, and `app/` directory there
4. Add the secrets above in Space Settings
5. The Space will build and expose the API at `https://your-username-docqa-api.hf.space`

## API endpoints

- `GET /health` — service status
- `POST /ingest` — upload a PDF (multipart/form-data, field: `file`)
- `POST /query` — ask a question (`{"question": "..."}`)
- `GET /docs` — Swagger UI
