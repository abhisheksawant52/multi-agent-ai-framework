"""Smoke tests that the public API imports and exposes expected symbols."""

from __future__ import annotations

import multi_agent


def test_version_exposed() -> None:
    assert isinstance(multi_agent.__version__, str)
    assert multi_agent.__version__.count(".") == 2


def test_public_api_symbols() -> None:
    for symbol in [
        "Agent",
        "LLMAgent",
        "Orchestrator",
        "Pattern",
        "Message",
        "Role",
        "ToolRegistry",
        "default_registry",
        "ConversationMemory",
        "SharedMemory",
    ]:
        assert hasattr(multi_agent, symbol), symbol
