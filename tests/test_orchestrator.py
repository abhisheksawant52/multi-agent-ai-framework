"""Unit tests for the orchestrator using offline dummy agents (no network)."""

from __future__ import annotations

from multi_agent.agent import Agent
from multi_agent.memory import SharedMemory
from multi_agent.message import Message
from multi_agent.orchestrator import Orchestrator, Pattern


class UppercaseAgent(Agent):
    """A deterministic dummy agent that uppercases its input."""

    def step(self, message: Message, context: SharedMemory | None = None) -> Message:
        reply = Message.assistant(message.content.upper(), name=self.name)
        if context is not None:
            context.set(f"{self.name}:last_reply", reply.content)
        return reply


class ExclaimAgent(Agent):
    """A dummy agent that appends an exclamation mark."""

    def step(self, message: Message, context: SharedMemory | None = None) -> Message:
        return Message.assistant(f"{message.content}!", name=self.name)


def test_sequential_pipeline_pipes_output() -> None:
    orchestrator = Orchestrator([UppercaseAgent("upper"), ExclaimAgent("bang")])
    result = orchestrator.run("hello", pattern=Pattern.SEQUENTIAL)
    assert result.content == "HELLO!"
    assert result.name == "bang"


def test_parallel_runs_each_agent_on_same_prompt() -> None:
    orchestrator = Orchestrator([UppercaseAgent("upper"), ExclaimAgent("bang")])
    replies = orchestrator.run_parallel("hi")
    contents = {m.content for m in replies}
    assert contents == {"HI", "hi!"}


def test_shared_memory_is_populated() -> None:
    orchestrator = Orchestrator([UppercaseAgent("upper")])
    orchestrator.run("data", pattern=Pattern.SEQUENTIAL)
    assert orchestrator.shared_memory.get("upper:last_reply") == "DATA"


def test_empty_agents_rejected() -> None:
    import pytest

    with pytest.raises(ValueError):
        Orchestrator([])
