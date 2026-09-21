"""Durable task scheduling primitives."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from enum import StrEnum
from typing import Callable

from croniter import croniter

from .errors import ValidationError
from .tasks import TaskManager


class ScheduleKind(StrEnum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    CRON = "cron"
    CUSTOM = "custom"


@dataclass(frozen=True, slots=True)
class ScheduleSpec:
    kind: ScheduleKind
    run_at: datetime | None = None
    at_time: time | None = None
    weekdays: frozenset[int] = frozenset()
    cron_expression: str | None = None
    custom_next: Callable[[datetime], datetime | None] | None = None

    def next_after(self, after: datetime) -> datetime | None:
        if after.tzinfo is None:
            raise ValidationError("scheduler datetimes must be timezone-aware")

        if self.kind is ScheduleKind.ONCE:
            if self.run_at is None or self.run_at.tzinfo is None:
                raise ValidationError("one-time schedule requires timezone-aware run_at")
            return self.run_at if self.run_at > after else None

        if self.kind is ScheduleKind.DAILY:
            if self.at_time is None:
                raise ValidationError("daily schedule requires at_time")
            candidate = datetime.combine(after.date(), self.at_time, tzinfo=after.tzinfo)
            return candidate if candidate > after else candidate + timedelta(days=1)

        if self.kind is ScheduleKind.WEEKLY:
            if self.at_time is None or not self.weekdays:
                raise ValidationError("weekly schedule requires at_time and weekdays")
            for offset in range(1, 8):
                candidate_date = after.date() + timedelta(days=offset)
                if candidate_date.weekday() in self.weekdays:
                    return datetime.combine(
                        candidate_date, self.at_time, tzinfo=after.tzinfo
                    )
            return None

        if self.kind is ScheduleKind.CRON:
            if not self.cron_expression:
                raise ValidationError("cron schedule requires an expression")
            iterator = croniter(self.cron_expression, after)
            candidate = iterator.get_next(datetime)
            if candidate.tzinfo is None:
                candidate = candidate.replace(tzinfo=after.tzinfo)
            return candidate

        if self.kind is ScheduleKind.CUSTOM:
            if self.custom_next is None:
                raise ValidationError("custom schedule requires custom_next")
            candidate = self.custom_next(after)
            if candidate is not None and candidate.tzinfo is None:
                raise ValidationError("custom schedule returned naive datetime")
            return candidate

        raise ValidationError("unsupported schedule kind")


class Scheduler:
    """Turns schedule definitions into durable task intents."""

    def __init__(self, task_manager: TaskManager) -> None:
        self.task_manager = task_manager

    def schedule(
        self,
        task_type: str,
        schedule: ScheduleSpec,
        payload: dict | None = None,
        *,
        owner_id: str | None = None,
        after: datetime | None = None,
        max_attempts: int = 1,
    ) -> str:
        reference = after or datetime.now(timezone.utc)
        due = schedule.next_after(reference)
        if due is None:
            raise ValidationError("schedule has no future occurrence")

        return self.task_manager.create(
            task_type,
            payload,
            owner_id=owner_id,
            scheduled_at=due,
            max_attempts=max_attempts,
        )

    @staticmethod
    def daily(at_time: time) -> ScheduleSpec:
        return ScheduleSpec(kind=ScheduleKind.DAILY, at_time=at_time)

    @staticmethod
    def weekly(at_time: time, weekdays: set[int]) -> ScheduleSpec:
        if any(day < 0 or day > 6 for day in weekdays):
            raise ValidationError("weekdays must be in range 0..6")
        return ScheduleSpec(
            kind=ScheduleKind.WEEKLY,
            at_time=at_time,
            weekdays=frozenset(weekdays),
        )

    @staticmethod
    def cron(expression: str) -> ScheduleSpec:
        if not croniter.is_valid(expression):
            raise ValidationError("invalid cron expression")
        return ScheduleSpec(
            kind=ScheduleKind.CRON,
            cron_expression=expression,
        )

    @staticmethod
    def once(run_at: datetime) -> ScheduleSpec:
        return ScheduleSpec(kind=ScheduleKind.ONCE, run_at=run_at)
