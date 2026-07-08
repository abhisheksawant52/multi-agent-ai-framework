"""Memory abstractions for conversation and shared cross-agent state.

Two collaborating pieces are provided:

* :class:`ConversationMemory` -- an ordered, per-conversation message buffer
  with an optional retention window.
* :class:`SharedMemory` -- a simple key/value blackboard that agents use to
  publish and read intermediate results during orchestration.

Both implement the :class:`BaseMemory` marker so alternative backends (Redis,
databases, vector stores) can be dropped in later.
"""

from __future__ import annotations

import abc
import threading
from typing import Any

from .message import Message


class BaseMemory(abc.ABC):
    """Marker base class for pluggable memory backends."""

    @abc.abstractmethod
    def clear(self) -> None:
        """Remove all stored state."""
        raise NotImplementedError


class ConversationMemory(BaseMemory):
    """An ordered buffer of conversation messages.

    Args:
        max_messages: Optional cap; when exceeded the oldest messages are
            dropped (a naive sliding window). ``None`` keeps everything.
    """

    def __init__(self, max_messages: int | None = None) -> None:
        self._messages: list[Message] = []
        self.max_messages = max_messages

    def add(self, message: Message) -> None:
        """Append a message, enforcing the retention window if configured."""
        self._messages.append(message)
        if self.max_messages is not None and len(self._messages) > self.max_messages:
            overflow = len(self._messages) - self.max_messages
            del self._messages[:overflow]

    def extend(self, messages: list[Message]) -> None:
        """Append multiple messages in order."""
        for message in messages:
            self.add(message)

    def history(self) -> list[Message]:
        """Return a copy of the stored messages in chronological order."""
        return list(self._messages)

    def __len__(self) -> int:
        return len(self._messages)

    def clear(self) -> None:
        """Drop all stored messages."""
        self._messages.clear()


class SharedMemory(BaseMemory):
    """Thread-safe key/value blackboard shared across agents."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self._lock = threading.Lock()

    def set(self, key: str, value: Any) -> None:
        """Store ``value`` under ``key``."""
        with self._lock:
            self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for ``key`` or ``default`` if absent."""
        with self._lock:
            return self._store.get(key, default)

    def snapshot(self) -> dict[str, Any]:
        """Return a shallow copy of the entire blackboard."""
        with self._lock:
            return dict(self._store)

    def clear(self) -> None:
        """Remove all shared entries."""
        with self._lock:
            self._store.clear()
