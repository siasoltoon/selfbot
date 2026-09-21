from selfbot.db import Database
from selfbot.models import SystemMetadata


def test_sqlite_database_ping_and_transaction(tmp_path):
    database = Database(f"sqlite:///{tmp_path / 'test.db'}")

    assert database.ping() is True

    database.create_schema_for_tests()
    with database.session() as session:
        session.add(SystemMetadata(key="environment", value="test"))

    with database.session() as session:
        item = session.get(SystemMetadata, "environment")

    assert item is not None
    assert item.value == "test"
