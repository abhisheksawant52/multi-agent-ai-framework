"""Runnable example: wire two agents into an orchestrated pipeline.

This example uses the offline :class:`EchoLLM`, so it runs without network
access or API keys. It demonstrates the sequential and parallel patterns and
shows a tool being invoked directly.

Run it with::

    python examples/two_agent_pipeline.py
"""

from __future__ import annotations

from multi_agent import (
    EchoLLM,
    LLMAgent,
    Orchestrator,
    Pattern,
    configure_logging,
    default_registry,
)


def build_orchestrator() -> Orchestrator:
    """Construct a researcher -> writer pipeline backed by the echo LLM."""
    llm = EchoLLM(model="demo-model")
    tools = default_registry()
    researcher = LLMAgent(
        name="researcher",
        system_prompt="You gather facts about a topic.",
        llm=llm,
        tools=tools,
    )
    writer = LLMAgent(
        name="writer",
        system_prompt="You turn research notes into a short summary.",
        llm=llm,
    )
    return Orchestrator(agents=[researcher, writer])


def main() -> None:
    """Run the example end to end."""
    configure_logging()
    orchestrator = build_orchestrator()

    prompt = "Explain multi-agent systems in one sentence."

    sequential = orchestrator.run(prompt, pattern=Pattern.SEQUENTIAL)
    print("Sequential result:")
    print(f"  {sequential.content}\n")

    parallel = orchestrator.run(prompt, pattern=Pattern.PARALLEL)
    print("Parallel result:")
    print(f"  {parallel.content}\n")

    calculator = orchestrator.agents[0].tools.get("calculator")
    print("Calculator tool: 2 * (3 + 4) =", calculator(expression="2 * (3 + 4)"))

    print("\nShared memory snapshot:")
    for key, value in orchestrator.shared_memory.snapshot().items():
        print(f"  {key} -> {value}")


if __name__ == "__main__":
    main()
