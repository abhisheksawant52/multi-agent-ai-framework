"""LLM provider client abstraction.

This module defines a small provider-agnostic interface (:class:`LLMClient`)
plus two reference implementations:

* :class:`EchoLLM` -- a deterministic, offline client used for tests, examples,
  and local development. It never performs network I/O.
* :class:`HTTPLLM` -- a thin ``httpx``-based client sketch that targets an
  OpenAI-compatible ``/chat/completions`` endpoint. The transport is wired up
  but the class is intentionally not exercised in tests (no live calls).

The abstraction keeps the rest of the framework independent of any specific
vendor SDK.
"""

from __future__ import annotations

import abc
from typing import Any

from .config import Settings, get_settings
from .logging_config import get_logger
from .message import Message, Role

logger = get_logger("llm")


class LLMClient(abc.ABC):
    """Abstract base class for chat-completion style LLM providers."""

    def __init__(self, model: str) -> None:
        self.model = model

    @abc.abstractmethod
    def complete(self, messages: list[Message], **kwargs: Any) -> Message:
        """Generate an assistant reply for the given conversation.

        Args:
            messages: Ordered conversation history.
            **kwargs: Provider-specific generation options (temperature, etc.).

        Returns:
            A new assistant :class:`Message`.
        """
        raise NotImplementedError


class EchoLLM(LLMClient):
    """Deterministic offline client that echoes the last user message.

    Useful for wiring up agents and orchestration without incurring API cost
    or requiring network access.
    """

    def complete(self, messages: list[Message], **kwargs: Any) -> Message:
        """Return an assistant message summarizing the latest user turn."""
        last_user = next(
            (m for m in reversed(messages) if m.role == Role.USER),
            None,
        )
        content = last_user.content if last_user else ""
        logger.debug("EchoLLM completing with model=%s", self.model)
        return Message.assistant(f"[echo:{self.model}] {content}")


class HTTPLLM(LLMClient):
    """OpenAI-compatible HTTP client sketch.

    The client is constructed lazily; :meth:`complete` builds a standard
    chat-completions payload. Network calls are not covered by the test suite.
    """

    def __init__(
        self,
        model: str,
        api_key: str | None,
        base_url: str,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(model)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def complete(self, messages: list[Message], **kwargs: Any) -> Message:
        """Call the provider's chat-completions endpoint and return the reply."""
        import httpx  # imported lazily so offline use never needs the transport

        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            **kwargs,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return Message.assistant(content)


def build_llm(settings: Settings | None = None) -> LLMClient:
    """Construct an :class:`LLMClient` from framework settings.

    Falls back to :class:`EchoLLM` when the provider is ``"echo"`` or when no
    base URL is configured, keeping local/offline usage friction-free.
    """
    settings = settings or get_settings()
    if settings.llm_provider == "echo" or not settings.llm_base_url:
        return EchoLLM(model=settings.llm_model)
    return HTTPLLM(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=settings.request_timeout_seconds,
    )
