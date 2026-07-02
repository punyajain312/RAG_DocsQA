"""Abstract LLM client interface — swap providers without changing the pipeline."""

from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Send a prompt and return the text response."""
        ...
