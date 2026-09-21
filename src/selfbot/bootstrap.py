"""Core runtime bootstrap without deployment-specific behavior."""

from __future__ import annotations

from dataclasses import dataclass

from .config import Settings, load_settings
from .db import Database
from .logging import configure_logging, get_logger
from .services import CoreServices


@dataclass(slots=True)
class Runtime:
    settings: Settings
    database: Database
    services: CoreServices


def create_runtime() -> Runtime:
    """Load validated settings and construct the shared core services."""

    settings = load_settings()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)
    database = Database(settings.database_url, echo=settings.database_echo)
    services = CoreServices.create(database, owner_id=settings.owner_id)
    logger.info(
        "core runtime initialized",
        extra={"context": {"environment": settings.environment}},
    )
    return Runtime(
        settings=settings,
        database=database,
        services=services,
    )
