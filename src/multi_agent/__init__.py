"""multi_agent -- a lightweight framework for building multi-agent AI systems.

Public API:

* Messaging: :class:`Message`, :class:`Role`.
* Agents: :class:`Agent`, :class:`LLMAgent`.
* Orchestration: :class:`Orchestrator`, :class:`Pattern`.
* Tools: :class:`Tool`, :class:`FunctionTool`, :class:`ToolRegistry`,
  :func:`default_registry`, :class:`CalculatorTool`, :class:`HTTPFetchTool`.
* Memory: :class:`ConversationMemory`, :class:`SharedMemory`.
* LLM: :class:`LLMClient`, :class:`EchoLLM`, :class:`HTTPLLM`, :func:`build_llm`.
* Config/logging: :class:`Settings`, :func:`get_settings`,
  :func:`configure_logging`.
"""

from __future__ import annotations

from .agent import Agent, LLMAgent
from .config import Settings, get_settings
from .llm import EchoLLM, HTTPLLM, LLMClient, build_llm
from .logging_config import configure_logging, get_logger
from .memory import ConversationMemory, SharedMemory
from .message import Message, Role
from .orchestrator import Orchestrator, Pattern
from .tools import (
    CalculatorTool,
    FunctionTool,
    HTTPFetchTool,
    Tool,
    ToolError,
    ToolRegistry,
    default_registry,
)

__version__ = "0.1.0"

__all__ = [
    "Agent",
    "LLMAgent",
    "Orchestrator",
    "Pattern",
    "Message",
    "Role",
    "Tool",
    "ToolError",
    "FunctionTool",
    "ToolRegistry",
    "default_registry",
    "CalculatorTool",
    "HTTPFetchTool",
    "ConversationMemory",
    "SharedMemory",
    "LLMClient",
    "EchoLLM",
    "HTTPLLM",
    "build_llm",
    "Settings",
    "get_settings",
    "configure_logging",
    "get_logger",
    "__version__",
]
