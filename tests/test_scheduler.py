from datetime import datetime, time, timezone

import pytest

from selfbot.db import Database
from selfbot.errors import ValidationError
from selfbot.scheduler import Scheduler, ScheduleKind, ScheduleSpec
from selfbot.tasks import TaskManager


def test_daily_schedule_moves_to_next_day():
    after = datetime(2026, 9, 21, 18, 0, tzinfo=timezone.utc)
    spec = Scheduler.daily(time(17, 0))

    next_run = spec.next_after(after)

    assert next_run == datetime(2026, 9, 22, 17, 0, tzinfo=timezone.utc)


def test_weekly_schedule():
    after = datetime(2026, 9, 21, 10, 0, tzinfo=timezone.utc)
    spec = Scheduler.weekly(time(9, 0), {0, 2})

    next_run = spec.next_after(after)

    assert next_run.weekday() == 2


def test_cron_schedule():
    after = datetime(2026, 9, 21, 10, 0, tzinfo=timezone.utc)
    spec = Scheduler.cron("0 12 * * *")

    next_run = spec.next_after(after)

    assert next_run.hour == 12


def test_scheduler_creates_durable_task(tmp_path):
    database = Database(f"sqlite:///{tmp_path / 'scheduler.db'}")
    database.create_schema_for_tests()

    scheduler = Scheduler(TaskManager(database))
    task_id = scheduler.schedule(
        "reminder",
        ScheduleSpec(
            kind=ScheduleKind.ONCE,
            run_at=datetime(2027, 1, 1, 12, 0, tzinfo=timezone.utc),
        ),
    )

    assert task_id
    assert TaskManager(database).get(task_id).task_type == "reminder"


def test_weekdays_are_validated():
    with pytest.raises(ValidationError):
        Scheduler.weekly(time(9, 0), {7})
