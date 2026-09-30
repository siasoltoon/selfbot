from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_honors_database_url(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "alembic-env.sqlite"
    database_url = f"sqlite:///{database_path.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)

    config = Config("alembic.ini")
    command.upgrade(config, "head")

    engine = create_engine(database_url)
    tables = set(inspect(engine).get_table_names())

    assert "alembic_version" in tables
    assert "system_metadata" in tables
    assert "tasks" in tables
    assert "domain_state" in tables
    assert "security_audit" in tables
    assert "telegram_accounts" in tables
    assert "diamond_wallets" in tables
    assert "diamond_transactions" in tables
