"""Core runtime bootstrap without deployment-specific behavior."""

from __future__ import annotations

from dataclasses import dataclass

from .config import Settings, load_settings
from .db import Database
from .logging import configure_logging, get_logger
from .economy import EconomyPolicy
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
    database = Database(
        settings.database_url,
        echo=settings.database_echo,
        connect_retries=settings.database_connect_retries,
        connect_retry_delay=settings.database_connect_retry_delay,
    )
    services = CoreServices.create(
        database,
        owner_id=settings.owner_id,
        economy_policy=EconomyPolicy(
            min_transfer=settings.diamond_min_transfer,
            max_transfer=settings.diamond_max_transfer,
            daily_transfer_limit=settings.diamond_daily_transfer_limit,
            fee_bps=settings.diamond_fee_bps,
            min_fee=settings.diamond_min_fee,
            max_fee=settings.diamond_max_fee,
            max_admin_adjustment=settings.diamond_max_admin_adjustment,
        ),
    )
    logger.info(
        "core runtime initialized",
        extra={"context": {"environment": settings.environment}},
    )
    return Runtime(
        settings=settings,
        database=database,
        services=services,
    )
