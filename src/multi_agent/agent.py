"""Agent base classes.

An :class:`Agent` consumes an input string plus shared context and produces an
:class:`~multi_agent.message.Message`. :class:`LLMAgent` is a concrete agent
that maintains conversation memory, delegates generation to an
:class:`~multi_agent.llm.LLMClient`, and can call registered tools.
"""

from __future__ import annotations

import abc
from typing import Any

from .llm import LLMClient, build_llm
from .logging_config import get_logger
from .memory import ConversationMemory, SharedMemory
from .message import Message, Role
from .tools import ToolRegistry

logger = get_logger("agent")


class Agent(abc.ABC):
    """Abstract base class for all agents.

    Attributes:
        name: A unique, human-readable identifier for the agent.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    @abc.abstractmethod
    def step(self, message: Message, context: SharedMemory | None = None) -> Message:
        """Perform a single reasoning step for one input message.

        Args:
            message: The incoming message to react to.
            context: Optional shared blackboard for cross-agent state.

        Returns:
            The agent's response message.
        """
        raise NotImplementedError

    def run(self, prompt: str, context: SharedMemory | None = None) -> Message:
        """Run the agent on a raw prompt string.

        This is a convenience wrapper that packages ``prompt`` into a user
        :class:`Message` and delegates to :meth:`step`.
        """
        logger.debug("Agent %s running prompt", self.name)
        return self.step(Message.user(prompt), context=context)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"{type(self).__name__}(name={self.name!r})"


class LLMAgent(Agent):
    """An agent backed by an LLM client with optional tool access.

    Args:
        name: Unique agent name.
        system_prompt: Instruction prepended to every conversation.
        llm: LLM client; defaults to one built from framework settings.
        tools: Optional tool registry the agent may dispatch to.
        memory: Optional conversation memory; created if omitted.
    """

    def __init__(
        self,
        name: str,
        system_prompt: str = "You are a helpful assistant.",
        llm: LLMClient | None = None,
        tools: ToolRegistry | None = None,
        memory: ConversationMemory | None = None,
    ) -> None:
        super().__init__(name)
        self.system_prompt = system_prompt
        self.llm = llm or build_llm()
        self.tools = tools
        self.memory = memory or ConversationMemory()
        if not self.memory.history():
            self.memory.add(Message.system(system_prompt))

    def use_tool(self, tool_name: str, **kwargs: Any) -> Message:
        """Invoke a registered tool and record the result as a tool message.

        Raises:
            RuntimeError: If the agent has no tool registry.
            KeyError: If the tool is not registered.
        """
        if self.tools is None:
            raise RuntimeError(f"Agent {self.name} has no tools configured")
        tool = self.tools.get(tool_name)
        result = tool(**kwargs)
        message = Message(role=Role.TOOL, content=str(result), name=tool_name)
        self.memory.add(message)
        return message

    def step(self, message: Message, context: SharedMemory | None = None) -> Message:
        """Append the input to memory, query the LLM, and store the reply."""
        self.memory.add(message)
        reply = self.llm.complete(self.memory.history())
        reply.name = self.name
        self.memory.add(reply)
        if context is not None:
            context.set(f"{self.name}:last_reply", reply.content)
        return reply
