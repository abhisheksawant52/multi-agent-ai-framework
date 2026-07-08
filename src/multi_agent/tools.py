"""Tool abstraction, a registry, and a couple of reference tools.

Agents invoke :class:`Tool` instances to take actions in the world. Tools are
registered in a :class:`ToolRegistry` (a global default registry is provided)
so they can be discovered and dispatched by name.
"""

from __future__ import annotations

import abc
import ast
import operator
from typing import Any, Callable

from .logging_config import get_logger

logger = get_logger("tools")


class ToolError(RuntimeError):
    """Raised when a tool fails to execute or receives invalid input."""


class Tool(abc.ABC):
    """Abstract base class for an executable tool.

    Subclasses set :attr:`name` and :attr:`description` and implement
    :meth:`run`. The description is intended to be surfaced to an LLM so it can
    decide when to call the tool.
    """

    name: str = ""
    description: str = ""

    @abc.abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """Execute the tool with keyword arguments and return a result."""
        raise NotImplementedError

    def __call__(self, **kwargs: Any) -> Any:
        logger.debug("Invoking tool %s with %s", self.name, kwargs)
        return self.run(**kwargs)


class FunctionTool(Tool):
    """Adapt a plain Python callable into a :class:`Tool`."""

    def __init__(self, name: str, description: str, func: Callable[..., Any]) -> None:
        self.name = name
        self.description = description
        self._func = func

    def run(self, **kwargs: Any) -> Any:
        return self._func(**kwargs)


class ToolRegistry:
    """A name-indexed collection of tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> Tool:
        """Register ``tool`` by its name.

        Raises:
            ValueError: If the tool has no name or the name is already taken.
        """
        if not tool.name:
            raise ValueError("Tool must define a non-empty name")
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        self._tools[tool.name] = tool
        return tool

    def get(self, name: str) -> Tool:
        """Return the tool registered under ``name``.

        Raises:
            KeyError: If no such tool exists.
        """
        if name not in self._tools:
            raise KeyError(f"No tool registered under '{name}'")
        return self._tools[name]

    def names(self) -> list[str]:
        """Return the sorted list of registered tool names."""
        return sorted(self._tools)

    def __contains__(self, name: object) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)


# --- Reference tools --------------------------------------------------------

_ALLOWED_BINOPS: dict[type[ast.operator], Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_ALLOWED_UNARYOPS: dict[type[ast.unaryop], Callable[[Any], Any]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class CalculatorTool(Tool):
    """Safely evaluate a basic arithmetic expression.

    Only numeric literals and the operators ``+ - * / ** %`` are permitted; the
    expression is parsed with :mod:`ast` and never passed to :func:`eval`.
    """

    name = "calculator"
    description = "Evaluate an arithmetic expression, e.g. '2 * (3 + 4)'."

    def run(self, expression: str) -> float:  # type: ignore[override]
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as exc:  # pragma: no cover - defensive
            raise ToolError(f"Invalid expression: {expression!r}") from exc
        return float(self._eval(tree.body))

    def _eval(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
            return _ALLOWED_BINOPS[type(node.op)](self._eval(node.left), self._eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
            return _ALLOWED_UNARYOPS[type(node.op)](self._eval(node.operand))
        raise ToolError("Unsupported expression element")


class HTTPFetchTool(Tool):
    """Fetch the body of an HTTP(S) URL.

    The ``httpx`` import is deferred so the rest of the framework remains
    importable and testable without performing any network I/O.
    """

    name = "http_fetch"
    description = "HTTP GET a URL and return the response text (truncated)."

    def __init__(self, timeout: float = 10.0, max_chars: int = 10_000) -> None:
        self.timeout = timeout
        self.max_chars = max_chars

    def run(self, url: str) -> str:  # type: ignore[override]
        import httpx

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.text[: self.max_chars]


def default_registry() -> ToolRegistry:
    """Return a registry pre-populated with the reference tools."""
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(HTTPFetchTool())
    return registry
