from datetime import datetime, timedelta, timezone

import pytest

from selfbot.db import Database
from selfbot.errors import ConflictError
from selfbot.task_models import TaskRecord, TaskStatus
from selfbot.tasks import TaskManager


def make_manager(tmp_path):
    database = Database(f"sqlite:///{tmp_path / 'tasks.db'}")
    database.create_schema_for_tests()
    return TaskManager(database)


def test_task_lifecycle_and_retry(tmp_path):
    manager = make_manager(tmp_path)

    task_id = manager.create(
        "demo",
        {"value": 1},
        max_attempts=2,
    )

    claimed = manager.claim_next()
    assert claimed is not None
    assert claimed.id == task_id
    assert claimed.status == TaskStatus.RUNNING.value
    assert claimed.attempts == 1

    status = manager.fail(task_id, "dependency_failure", "temporary")
    assert status is TaskStatus.QUEUED

    claimed_again = manager.claim_next()
    assert claimed_again is not None
    assert claimed_again.attempts == 2

    manager.complete(task_id, {"ok": True})
    assert manager.get(task_id).status == TaskStatus.SUCCEEDED.value


def test_task_cancellation(tmp_path):
    manager = make_manager(tmp_path)
    task_id = manager.create("cancel-me")

    manager.cancel(task_id)

    assert manager.get(task_id).status == TaskStatus.CANCELLED.value


def test_complete_requires_running_task(tmp_path):
    manager = make_manager(tmp_path)
    task_id = manager.create("not-running")

    with pytest.raises(ConflictError):
        manager.complete(task_id)
