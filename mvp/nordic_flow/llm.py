"""Minimal Groq client (OpenAI-compatible chat API). The key comes from GROQ_API_KEY only; it is never stored.

Free-tier model names change over time, so the model is configurable with GROQ_MODEL.
"""
from __future__ import annotations
import os
import httpx

DEFAULT_MODEL = "llama-3.3-70b-versatile"
BASE_URL = "https://api.groq.com/openai/v1/chat/completions"


class LLMError(RuntimeError):
    pass


class GroqClient:
    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: float = 20.0):
        self.api_key = api_key if api_key is not None else os.environ.get("GROQ_API_KEY", "")
        self.model = model or os.environ.get("GROQ_MODEL", DEFAULT_MODEL)
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: list[dict], temperature: float = 0.2, max_tokens: int = 400) -> str:
        if not self.enabled:
            raise LLMError("GROQ_API_KEY is not set")
        try:
            r = httpx.post(BASE_URL, timeout=self.timeout,
                           headers={"Authorization": f"Bearer {self.api_key}"},
                           json={"model": self.model, "messages": messages,
                                 "temperature": temperature, "max_tokens": max_tokens})
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as e:
            raise LLMError(f"LLM request failed: {type(e).__name__}") from e
