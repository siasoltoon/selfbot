"""Environment-backed configuration for the application."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .errors import ConfigurationError


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ConfigurationError(f"{name} must be a boolean value")


@dataclass(frozen=True, slots=True)
class Settings:
    environment: str
    log_level: str
    database_url: str
    database_echo: bool
    telegram_api_id: str | None
    telegram_api_hash: str | None
    telegram_session: str | None
    pc_worker_enabled: bool
    pc_worker_url: str | None
    pc_worker_token: str | None


def load_settings() -> Settings:
    environment = os.getenv("SELF_BOT_ENV", "development").strip().lower()
    if environment not in {"development", "test", "production"}:
        raise ConfigurationError("SELF_BOT_ENV must be development, test, or production")

    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ConfigurationError("LOG_LEVEL must be a standard logging level")

    database_url = os.getenv("DATABASE_URL", "sqlite:///./data/selfbot.db").strip()
    if not database_url:
        raise ConfigurationError("DATABASE_URL must not be empty")
    if not database_url.startswith(("sqlite://", "postgresql://", "postgresql+")):
        raise ConfigurationError("DATABASE_URL must use SQLite or PostgreSQL")

    worker_enabled = _bool_env("PC_WORKER_ENABLED", False)
    worker_url = os.getenv("PC_WORKER_URL")
    worker_token = os.getenv("PC_WORKER_TOKEN")

    if worker_enabled and not worker_url:
        raise ConfigurationError("PC_WORKER_URL is required when PC_WORKER_ENABLED=true")
    if worker_enabled and not worker_token:
        raise ConfigurationError("PC_WORKER_TOKEN is required when PC_WORKER_ENABLED=true")

    return Settings(
        environment=environment,
        log_level=log_level,
        database_url=database_url,
        database_echo=_bool_env("DATABASE_ECHO", False),
        telegram_api_id=os.getenv("TELEGRAM_API_ID") or None,
        telegram_api_hash=os.getenv("TELEGRAM_API_HASH") or None,
        telegram_session=os.getenv("TELEGRAM_SESSION") or None,
        pc_worker_enabled=worker_enabled,
        pc_worker_url=worker_url,
        pc_worker_token=worker_token,
    )
