from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_head(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    root = Path(__file__).resolve().parents[1]
    database_url = f"sqlite:///{tmp_path / 'migration.db'}"

    config = Config(str(root / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    tables = inspect(engine).get_table_names()

    assert "alembic_version" in tables
    assert "system_metadata" in tables
    assert "tasks" in tables
    assert "domain_state" in tables
    assert "security_audit" in tables
    assert "telegram_accounts" in tables
    assert "diamond_wallets" in tables
    assert "diamond_transactions" in tables
