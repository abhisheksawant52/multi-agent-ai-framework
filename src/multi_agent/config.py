"""Runtime configuration for the multi-agent framework.

Settings are loaded from environment variables (optionally via a ``.env`` file)
using :mod:`pydantic_settings`. All variables are prefixed with ``AGENT_``.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Framework-wide configuration.

    Attributes:
        llm_provider: Identifier of the LLM provider to use (e.g. ``"echo"``).
        llm_model: Model name passed to the provider client.
        llm_api_key: API key/token for the provider. Never commit real values.
        llm_base_url: Optional base URL override for self-hosted gateways.
        request_timeout_seconds: Per-request timeout for provider calls.
        max_steps: Safety cap on reasoning/tool-use steps per agent run.
        log_level: Root log level for the framework.
        log_json: Emit structured JSON logs when ``True``.
    """

    model_config = SettingsConfigDict(
        env_prefix="AGENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: str = "echo"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    request_timeout_seconds: float = Field(default=30.0, gt=0)

    max_steps: int = Field(default=8, ge=1)

    log_level: str = "INFO"
    log_json: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance loaded from the environment."""
    return Settings()
