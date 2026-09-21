"""Durable task lifecycle service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update

from .db import Database
from .errors import ConflictError, NotFoundError, ValidationError
from .task_models import TaskRecord, TaskStatus


class TaskManager:
    """Creates and transitions durable tasks."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        task_type: str,
        payload: dict[str, Any] | None = None,
        *,
        owner_id: str | None = None,
        scheduled_at: datetime | None = None,
        max_attempts: int = 1,
    ) -> str:
        if not task_type.strip():
            raise ValidationError("task_type must not be empty")
        if max_attempts < 1:
            raise ValidationError("max_attempts must be at least 1")
        due = scheduled_at or datetime.now(timezone.utc)
        if due.tzinfo is None:
            raise ValidationError("scheduled_at must be timezone-aware")

        record = TaskRecord(
            task_type=task_type,
            owner_id=owner_id,
            status=TaskStatus.QUEUED.value,
            payload=dict(payload or {}),
            scheduled_at=due,
            max_attempts=max_attempts,
        )
        with self.database.session() as session:
            session.add(record)
            session.flush()
            return record.id

    def get(self, task_id: str) -> TaskRecord:
        with self.database.session() as session:
            record = session.get(TaskRecord, task_id)
            if record is None:
                raise NotFoundError(f"task not found: {task_id}")
            session.expunge(record)
            return record

    def claim_next(self, now: datetime | None = None) -> TaskRecord | None:
        due = now or datetime.now(timezone.utc)
        if due.tzinfo is None:
            raise ValidationError("now must be timezone-aware")

        with self.database.session() as session:
            candidate = session.scalar(
                select(TaskRecord)
                .where(
                    TaskRecord.status == TaskStatus.QUEUED.value,
                    TaskRecord.scheduled_at <= due,
                )
                .order_by(TaskRecord.scheduled_at, TaskRecord.created_at)
                .limit(1)
            )
            if candidate is None:
                return None

            changed = session.execute(
                update(TaskRecord)
                .where(
                    TaskRecord.id == candidate.id,
                    TaskRecord.status == TaskStatus.QUEUED.value,
                )
                .values(
                    status=TaskStatus.RUNNING.value,
                    attempts=TaskRecord.attempts + 1,
                    updated_at=due,
                )
            )
            if changed.rowcount != 1:
                return None

            session.flush()
            session.refresh(candidate)
            session.expunge(candidate)
            return candidate

    def complete(self, task_id: str, result: dict[str, Any] | None = None) -> None:
        self._transition(
            task_id,
            from_status=TaskStatus.RUNNING,
            to_status=TaskStatus.SUCCEEDED,
            result=dict(result or {}),
            error_code=None,
            error_message=None,
        )

    def fail(self, task_id: str, code: str, message: str) -> TaskStatus:
        with self.database.session() as session:
            record = session.get(TaskRecord, task_id)
            if record is None:
                raise NotFoundError(f"task not found: {task_id}")
            if record.status != TaskStatus.RUNNING.value:
                raise ConflictError("only running tasks can fail")

            if record.attempts < record.max_attempts:
                record.status = TaskStatus.QUEUED.value
                final_status = TaskStatus.QUEUED
            else:
                record.status = TaskStatus.FAILED.value
                final_status = TaskStatus.FAILED

            record.error_code = code
            record.error_message = message
            return final_status

    def cancel(self, task_id: str) -> None:
        self._transition(
            task_id,
            from_status=(TaskStatus.QUEUED, TaskStatus.RUNNING),
            to_status=TaskStatus.CANCELLED,
            result=None,
        )

    def _transition(
        self,
        task_id: str,
        *,
        from_status: TaskStatus | tuple[TaskStatus, ...],
        to_status: TaskStatus,
        result: dict[str, Any] | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> None:
        allowed = (
            tuple(item.value for item in from_status)
            if isinstance(from_status, tuple)
            else (from_status.value,)
        )
        with self.database.session() as session:
            record = session.get(TaskRecord, task_id)
            if record is None:
                raise NotFoundError(f"task not found: {task_id}")
            if record.status not in allowed:
                raise ConflictError(
                    f"task {task_id} cannot transition from {record.status}"
                )
            record.status = to_status.value
            record.result = result
            record.error_code = error_code
            record.error_message = error_message
