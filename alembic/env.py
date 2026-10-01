"""Alembic environment for the application schema."""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from selfbot.db import Base, connect_with_retries  # noqa: E402
from selfbot.domain_models import DomainState, SecurityAuditRecord  # noqa: F401,E402
from selfbot.economy_models import DiamondTransaction, DiamondWallet  # noqa: F401,E402
from selfbot.models import SystemMetadata  # noqa: F401,E402
from selfbot.multi_user_models import TelegramAccount  # noqa: F401,E402
from selfbot.task_models import TaskRecord  # noqa: F401,E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

target_metadata = Base.metadata


def _database_connect_retries() -> int:
    return int(os.getenv("DATABASE_CONNECT_RETRIES", "3"))


def _database_connect_retry_delay() -> float:
    return float(os.getenv("DATABASE_CONNECT_RETRY_DELAY", "1.0"))


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=(
            {"timeout": 10}
            if (config.get_main_option("sqlalchemy.url") or "").startswith("mssql+pyodbc")
            else {}
        ),
    )
    with connect_with_retries(
        connectable,
        retries=_database_connect_retries(),
        retry_delay=_database_connect_retry_delay(),
    ) as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
