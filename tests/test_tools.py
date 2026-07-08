"""Unit tests for the tool registry and reference tools."""

from __future__ import annotations

import pytest

from multi_agent.tools import (
    CalculatorTool,
    FunctionTool,
    ToolError,
    ToolRegistry,
    default_registry,
)


def test_default_registry_contains_reference_tools() -> None:
    registry = default_registry()
    assert "calculator" in registry
    assert "http_fetch" in registry
    assert registry.names() == ["calculator", "http_fetch"]


def test_registry_rejects_duplicate_names() -> None:
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    with pytest.raises(ValueError):
        registry.register(CalculatorTool())


def test_registry_get_missing_raises() -> None:
    registry = ToolRegistry()
    with pytest.raises(KeyError):
        registry.get("nope")


def test_calculator_evaluates_expression() -> None:
    calc = CalculatorTool()
    assert calc(expression="2 * (3 + 4)") == 14.0
    assert calc(expression="-2 ** 3") == -8.0


def test_calculator_rejects_unsafe_expression() -> None:
    calc = CalculatorTool()
    with pytest.raises(ToolError):
        calc(expression="__import__('os').system('echo hi')")


def test_function_tool_wraps_callable() -> None:
    tool = FunctionTool("upper", "Uppercase text", lambda text: text.upper())
    assert tool(text="hello") == "HELLO"
