from selfbot.db import Database
from selfbot.services import CoreServices


def test_core_services_share_database_and_task_scheduler(tmp_path):
    database = Database(f"sqlite:///{tmp_path / 'services.db'}")
    services = CoreServices.create(database)

    assert services.database is database
    assert services.tasks.database is database
    assert services.scheduler.task_manager is services.tasks
    assert services.events is not None
    assert services.commands is not None
    assert services.plugins is not None
