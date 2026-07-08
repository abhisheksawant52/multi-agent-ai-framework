"""Orchestration patterns for coordinating multiple agents.

The :class:`Orchestrator` supports three collaboration patterns:

* **sequential** -- agents form a pipeline; each agent's output becomes the
  next agent's input.
* **parallel** -- every agent independently processes the same prompt and all
  replies are collected.
* **supervisor** -- a designated supervisor agent decides (in this reference
  implementation, round-robins) which worker handles the prompt, then
  summarizes the result.

All patterns share a :class:`~multi_agent.memory.SharedMemory` blackboard so
agents can read each other's intermediate output.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from .agent import Agent
from .logging_config import get_logger
from .memory import SharedMemory
from .message import Message

logger = get_logger("orchestrator")


class Pattern(str, Enum):
    """Supported orchestration patterns."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    SUPERVISOR = "supervisor"


class Orchestrator:
    """Coordinate a set of agents according to a chosen :class:`Pattern`.

    Args:
        agents: The worker agents to coordinate. Must be non-empty.
        supervisor: Agent used to summarize results in the supervisor pattern.
            Defaults to the first worker when omitted.
        max_workers: Thread-pool size for the parallel pattern.
    """

    def __init__(
        self,
        agents: list[Agent],
        supervisor: Agent | None = None,
        max_workers: int = 4,
    ) -> None:
        if not agents:
            raise ValueError("Orchestrator requires at least one agent")
        self.agents = agents
        self.supervisor = supervisor or agents[0]
        self.max_workers = max_workers
        self.shared_memory = SharedMemory()

    def run(self, prompt: str, pattern: Pattern = Pattern.SEQUENTIAL) -> Message:
        """Execute ``prompt`` under the given ``pattern`` and return the result.

        For sequential and supervisor patterns a single :class:`Message` is
        returned. For the parallel pattern the replies are concatenated into a
        single assistant message; use :meth:`run_parallel` for the raw list.
        """
        logger.info("Running orchestrator pattern=%s agents=%d", pattern, len(self.agents))
        if pattern == Pattern.SEQUENTIAL:
            return self._run_sequential(prompt)
        if pattern == Pattern.PARALLEL:
            replies = self.run_parallel(prompt)
            combined = "\n".join(f"{m.name}: {m.content}" for m in replies)
            return Message.assistant(combined, name="orchestrator")
        if pattern == Pattern.SUPERVISOR:
            return self._run_supervisor(prompt)
        raise ValueError(f"Unknown pattern: {pattern}")  # pragma: no cover

    def _run_sequential(self, prompt: str) -> Message:
        """Pipe the prompt through each agent in order."""
        current = prompt
        reply: Message | None = None
        for agent in self.agents:
            reply = agent.run(current, context=self.shared_memory)
            current = reply.content
        assert reply is not None  # guaranteed: agents is non-empty
        return reply

    def run_parallel(self, prompt: str) -> list[Message]:
        """Run every agent on the same prompt concurrently and collect replies."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = [
                pool.submit(agent.run, prompt, self.shared_memory) for agent in self.agents
            ]
            return [future.result() for future in futures]

    def _run_supervisor(self, prompt: str) -> Message:
        """Delegate to a worker, then have the supervisor summarize the result."""
        worker = self.agents[0]
        worker_reply = worker.run(prompt, context=self.shared_memory)
        summary_prompt = f"Summarize this result from {worker.name}: {worker_reply.content}"
        return self.supervisor.run(summary_prompt, context=self.shared_memory)
