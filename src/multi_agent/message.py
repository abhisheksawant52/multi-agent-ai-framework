"""Core message primitives exchanged between agents and LLM providers.

The framework models a conversation as an ordered list of :class:`Message`
objects. Roles follow the widely adopted chat-completion convention so that
messages can be handed to most LLM providers with minimal translation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Role(str, Enum):
    """The author role of a :class:`Message`.

    Values are plain strings so a message can be serialized directly into the
    payload expected by chat-completion style APIs.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass(slots=True)
class Message:
    """A single turn in a conversation.

    Attributes:
        role: The author of the message.
        content: The textual content of the message.
        name: Optional author name (e.g. the agent or tool that produced it).
        metadata: Arbitrary structured data attached to the message.
        created_at: Unix timestamp (seconds) of when the message was created.
    """

    role: Role
    content: str
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the message."""
        payload: dict[str, Any] = {"role": self.role.value, "content": self.content}
        if self.name is not None:
            payload["name"] = self.name
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload

    @classmethod
    def system(cls, content: str, **kwargs: Any) -> "Message":
        """Construct a system message."""
        return cls(role=Role.SYSTEM, content=content, **kwargs)

    @classmethod
    def user(cls, content: str, **kwargs: Any) -> "Message":
        """Construct a user message."""
        return cls(role=Role.USER, content=content, **kwargs)

    @classmethod
    def assistant(cls, content: str, **kwargs: Any) -> "Message":
        """Construct an assistant message."""
        return cls(role=Role.ASSISTANT, content=content, **kwargs)
