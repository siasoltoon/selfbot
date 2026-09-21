"""Core runtime bootstrap without Telegram or deployment-specific behavior."""

from __future__ import annotations

from dataclasses import dataclass

from .config import Settings, load_settings
from .db import Database
from .logging import configure_logging, get_logger


@dataclass(slots=True)
class Runtime:
    settings: Settings
    database: Database


def create_runtime() -> Runtime:
    """Load validated settings, configure logging and construct persistence."""

    settings = load_settings()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)
    database = Database(settings.database_url, echo=settings.database_echo)
    logger.info("core runtime initialized", extra={"context": {"environment": settings.environment}})
    return Runtime(settings=settings, database=database)
