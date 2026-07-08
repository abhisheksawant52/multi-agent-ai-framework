"""Logging configuration helpers for the multi-agent framework."""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

from .config import Settings, get_settings


class JsonFormatter(logging.Formatter):
    """A minimal structured JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003 - stdlib name
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging(settings: Settings | None = None) -> None:
    """Configure the root logger according to ``settings``.

    Args:
        settings: Optional settings object. Falls back to :func:`get_settings`.
    """
    settings = settings or get_settings()
    handler = logging.StreamHandler(stream=sys.stdout)
    if settings.log_json:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s")
        )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger under the ``multi_agent`` root."""
    return logging.getLogger(f"multi_agent.{name}")
