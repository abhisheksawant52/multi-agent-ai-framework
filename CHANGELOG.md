# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-08

### Added

- Core messaging primitives (`Message`, `Role`).
- Agent base class and `LLMAgent` with conversation memory and tool access.
- `Orchestrator` supporting sequential, parallel, and supervisor patterns.
- Tool abstraction, registry, and reference tools (`CalculatorTool`,
  `HTTPFetchTool`).
- Conversation and shared-memory stores.
- Provider-agnostic LLM client abstraction with offline `EchoLLM` and an
  `httpx`-based `HTTPLLM` sketch.
- `agentctl` command-line interface (version, tools, run).
- Runnable two-agent orchestration example.
- Terraform module for an ECR repository and an SQS agent task queue, with
  dev/prod environments.
- Multi-stage, non-root Dockerfile running the example.
- Test suite, CI pipeline, pre-commit hooks, and open-source project files.
