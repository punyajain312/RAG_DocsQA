"""Ollama local LLM client (fallback when no Anthropic key)."""

import logging

import httpx

from .base import LLMClient

logger = logging.getLogger(__name__)


class OllamaClient(LLMClient):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self._base_url = base_url.rstrip("/")
        self._model = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        logger.debug("Calling Ollama model '%s'", self._model)
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }
        response = httpx.post(
            f"{self._base_url}/api/chat",
            json=payload,
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
