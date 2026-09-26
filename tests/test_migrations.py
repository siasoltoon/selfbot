from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_head(tmp_path):
    root = Path(__file__).resolve().parents[1]
    database_url = f"sqlite:///{tmp_path / 'migration.db'}"

    config = Config(str(root / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    tables = inspect(engine).get_table_names()

    assert "alembic_version" in tables
    assert "system_metadata" in tables
    assert "tasks" in tables\n    assert "domain_state" in tables\n    assert "security_audit" in tables\n    assert "telegram_accounts" in tables\n    assert "diamond_wallets" in tables\n    assert "diamond_transactions" in tables
