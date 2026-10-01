"""Environment-backed configuration for the application."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .errors import ConfigurationError


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value.strip())
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer") from exc


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
    database_connect_retries: int = 3
    database_connect_retry_delay: float = 1.0
    owner_id: str | None = None
    telegram_session_is_string: bool = True
    telegram_onboarding_bot_token: str | None = None
    telegram_session_encryption_key: str | None = None
    diamond_min_transfer: int = 1
    diamond_max_transfer: int = 1000
    diamond_daily_transfer_limit: int = 3000
    diamond_fee_bps: int = 100
    diamond_min_fee: int = 1
    diamond_max_fee: int = 100
    diamond_max_admin_adjustment: int = 100000
    myoi_bot_username: str = "MeowieeeQBot"


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
    if not database_url.startswith(("sqlite://", "postgresql://", "postgresql+", "mssql+pyodbc://")):
        raise ConfigurationError("DATABASE_URL must use SQLite, PostgreSQL, or SQL Server via mssql+pyodbc")

    database_connect_retries = _int_env("DATABASE_CONNECT_RETRIES", 3)
    if database_connect_retries < 0 or database_connect_retries > 10:
        raise ConfigurationError("DATABASE_CONNECT_RETRIES must be between 0 and 10")
    try:
        database_connect_retry_delay = float(os.getenv("DATABASE_CONNECT_RETRY_DELAY", "1.0"))
    except ValueError as exc:
        raise ConfigurationError("DATABASE_CONNECT_RETRY_DELAY must be a number") from exc
    if database_connect_retry_delay < 0 or database_connect_retry_delay > 30:
        raise ConfigurationError("DATABASE_CONNECT_RETRY_DELAY must be between 0 and 30")

    worker_enabled = _bool_env("PC_WORKER_ENABLED", False)
    worker_url = os.getenv("PC_WORKER_URL")
    worker_token = os.getenv("PC_WORKER_TOKEN")
    owner_id = os.getenv("OWNER_ID") or None

    if worker_enabled and not worker_url:
        raise ConfigurationError("PC_WORKER_URL is required when PC_WORKER_ENABLED=true")
    if worker_enabled and not worker_token:
        raise ConfigurationError("PC_WORKER_TOKEN is required when PC_WORKER_ENABLED=true")

    diamond_min_transfer = _int_env("DIAMOND_MIN_TRANSFER", 1)
    diamond_max_transfer = _int_env("DIAMOND_MAX_TRANSFER", 1000)
    diamond_daily_transfer_limit = _int_env("DIAMOND_DAILY_TRANSFER_LIMIT", 3000)
    diamond_fee_bps = _int_env("DIAMOND_FEE_BPS", 100)
    diamond_min_fee = _int_env("DIAMOND_MIN_FEE", 1)
    diamond_max_fee = _int_env("DIAMOND_MAX_FEE", 100)
    diamond_max_admin_adjustment = _int_env("DIAMOND_MAX_ADMIN_ADJUSTMENT", 100000)
    if diamond_min_transfer < 1 or diamond_max_transfer < diamond_min_transfer:
        raise ConfigurationError("diamond transfer range is invalid")
    if diamond_daily_transfer_limit < diamond_max_transfer:
        raise ConfigurationError("diamond daily transfer limit must cover max transfer")
    if not 0 <= diamond_fee_bps <= 10000:
        raise ConfigurationError("DIAMOND_FEE_BPS must be between 0 and 10000")
    if diamond_min_fee < 0 or diamond_max_fee < diamond_min_fee:
        raise ConfigurationError("diamond fee range is invalid")
    if diamond_max_admin_adjustment < 1:
        raise ConfigurationError("DIAMOND_MAX_ADMIN_ADJUSTMENT must be positive")

    myoi_bot_username = (os.getenv("MYOI_BOT_USERNAME") or "MeowieeeQBot").strip().lstrip("@")
    if not myoi_bot_username:
        raise ConfigurationError("MYOI_BOT_USERNAME must not be empty")

    return Settings(
        environment=environment,
        log_level=log_level,
        database_url=database_url,
        database_echo=_bool_env("DATABASE_ECHO", False),
        database_connect_retries=database_connect_retries,
        database_connect_retry_delay=database_connect_retry_delay,
        telegram_api_id=os.getenv("TELEGRAM_API_ID") or None,
        telegram_api_hash=os.getenv("TELEGRAM_API_HASH") or None,
        telegram_session=os.getenv("TELEGRAM_SESSION") or None,
        telegram_session_is_string=_bool_env("TELEGRAM_SESSION_IS_STRING", True),
        pc_worker_enabled=worker_enabled,
        pc_worker_url=worker_url,
        pc_worker_token=worker_token,
        owner_id=owner_id,
        telegram_onboarding_bot_token=os.getenv("TELEGRAM_ONBOARDING_BOT_TOKEN") or None,
        telegram_session_encryption_key=os.getenv("TELEGRAM_SESSION_ENCRYPTION_KEY") or None,
        diamond_min_transfer=diamond_min_transfer,
        diamond_max_transfer=diamond_max_transfer,
        diamond_daily_transfer_limit=diamond_daily_transfer_limit,
        diamond_fee_bps=diamond_fee_bps,
        diamond_min_fee=diamond_min_fee,
        diamond_max_fee=diamond_max_fee,
        diamond_max_admin_adjustment=diamond_max_admin_adjustment,
        myoi_bot_username=myoi_bot_username,
    )
