# Architecture

`multi_agent` is a small, composable library. The dependency direction flows
from high-level coordination down to primitives, with no cycles:

```
cli -> orchestrator -> agent -> llm -> message
                         |        \
                         v         -> config -> (env)
                       memory
                         ^
tools --------------------
```

## Layers

- **message** — `Message` and `Role` dataclasses/enums, the wire format shared by
  every other module. Depends on nothing framework-internal.
- **config / logging_config** — `pydantic-settings` configuration and logging
  setup. Read by clients and agents.
- **llm** — provider-agnostic `LLMClient`. `EchoLLM` is fully offline;
  `HTTPLLM` targets an OpenAI-compatible endpoint. `build_llm()` selects one
  from settings.
- **tools** — `Tool` base class, `ToolRegistry`, and reference tools
  (`CalculatorTool`, `HTTPFetchTool`). Tools are dispatched by name.
- **memory** — `ConversationMemory` (per-conversation buffer) and `SharedMemory`
  (thread-safe cross-agent blackboard).
- **agent** — `Agent` abstract base and the concrete `LLMAgent`, which combines
  an LLM client, optional tools, and conversation memory.
- **orchestrator** — `Orchestrator` coordinates multiple agents using the
  `sequential`, `parallel`, and `supervisor` patterns over a shared blackboard.
- **cli** — the `agentctl` entry point.

## Infrastructure

The `terraform/` module provisions the runtime surface for a deployed agent
worker: an ECR repository for the container image (built from the `Dockerfile`)
and an SQS task queue with a dead-letter queue for durable task hand-off. See
the root module and `modules/agent_queue`.
