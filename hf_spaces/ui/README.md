---
title: DocQA
emoji: 📋
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: 1.35.0
app_file: app.py
pinned: false
---

# DocQA — Document Q&A UI

Streamlit frontend for the RAG DocQA system.

**Set the `API_URL` Space secret** to point at your deployed FastAPI backend
(e.g. `https://your-app.onrender.com`).

Without it the UI defaults to `http://localhost:8000`, which only works locally.
