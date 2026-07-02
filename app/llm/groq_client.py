"""Groq LLM client — free-tier cloud inference, OpenAI-compatible API.

Get a free API key at console.groq.com (no credit card needed).
Recommended model: llama-3.3-70b-versatile (free, fast, high quality).
"""

import logging

import httpx

from .base import LLMClient

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqClient(LLMClient):
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self._api_key = api_key
        self._model = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        logger.debug("Calling Groq model '%s'", self._model)
        response = httpx.post(
            GROQ_API_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.0,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
