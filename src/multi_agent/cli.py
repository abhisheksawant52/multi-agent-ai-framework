"""``agentctl`` -- a small command-line interface for the framework.

Commands:

* ``agentctl version`` -- print the installed framework version.
* ``agentctl tools`` -- list the tools in the default registry.
* ``agentctl run`` -- run a prompt through a pair of agents using a chosen
  orchestration pattern (uses the offline echo LLM by default).
"""

from __future__ import annotations

import click

from . import __version__
from .agent import LLMAgent
from .config import get_settings
from .llm import build_llm
from .logging_config import configure_logging
from .orchestrator import Orchestrator, Pattern
from .tools import default_registry


@click.group()
def main() -> None:
    """Entry point for the ``agentctl`` command-line tool."""
    configure_logging(get_settings())


@main.command()
def version() -> None:
    """Print the framework version."""
    click.echo(__version__)


@main.command()
def tools() -> None:
    """List the tools available in the default registry."""
    registry = default_registry()
    for name in registry.names():
        click.echo(f"{name}\t{registry.get(name).description}")


@main.command()
@click.argument("prompt")
@click.option(
    "--pattern",
    type=click.Choice([p.value for p in Pattern]),
    default=Pattern.SEQUENTIAL.value,
    help="Orchestration pattern to use.",
)
def run(prompt: str, pattern: str) -> None:
    """Run PROMPT through a two-agent orchestrator and print the result."""
    llm = build_llm()
    researcher = LLMAgent("researcher", "You research topics.", llm=llm)
    writer = LLMAgent("writer", "You write concise summaries.", llm=llm)
    orchestrator = Orchestrator([researcher, writer])
    reply = orchestrator.run(prompt, pattern=Pattern(pattern))
    click.echo(reply.content)


if __name__ == "__main__":  # pragma: no cover
    main()
