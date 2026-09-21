"""Reminder domain with explicit timezone-aware scheduling data."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import uuid4
from .errors import ValidationError

class ReminderStatus(StrEnum):
    PENDING="pending"; COMPLETED="completed"; CANCELLED="cancelled"

@dataclass(slots=True)
class Reminder:
    owner_id: str
    text: str
    due_at: datetime
    reminder_id: str = field(default_factory=lambda: str(uuid4()))
    recurrence: str | None = None
    status: ReminderStatus = ReminderStatus.PENDING
    timezone: str = "UTC"

class ReminderService:
    def __init__(self) -> None: self._items: dict[str, Reminder] = {}
    def create(self, owner_id: str, text: str, due_at: datetime, *, recurrence: str | None = None, timezone: str = "UTC") -> Reminder:
        if not owner_id.strip() or not text.strip(): raise ValidationError("owner_id and text are required")
        if due_at.tzinfo is None: raise ValidationError("due_at must be timezone-aware")
        if recurrence is not None and not recurrence.strip(): raise ValidationError("recurrence must not be empty")
        item=Reminder(owner_id,text,due_at,recurrence=recurrence,timezone=timezone)
        self._items[item.reminder_id]=item
        return item
    def list(self, owner_id: str) -> tuple[Reminder, ...]:
        return tuple(x for x in self._items.values() if x.owner_id==owner_id)
    def complete(self, owner_id: str, reminder_id: str) -> None:
        item=self._items.get(reminder_id)
        if item is None or item.owner_id != owner_id: raise ValidationError("reminder not found")
        item.status=ReminderStatus.COMPLETED
    def cancel(self, owner_id: str, reminder_id: str) -> None:
        item=self._items.get(reminder_id)
        if item is None or item.owner_id != owner_id: raise ValidationError("reminder not found")
        item.status=ReminderStatus.CANCELLED
