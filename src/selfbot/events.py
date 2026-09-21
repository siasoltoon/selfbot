"""Normalized internal event envelope and router."""

from __future__ import annotations

import inspect
from collections import defaultdict
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .errors import AppError, ValidationError, classify_error

EventHandler = Callable[["EventEnvelope"], Any]


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    event_type: str
    source: str
    payload: Mapping[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    actor_id: str | None = None
    chat_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_type.strip():
            raise ValidationError("event_type must not be empty")
        if not self.source.strip():
            raise ValidationError("event source must not be empty")
        if self.occurred_at.tzinfo is None:
            raise ValidationError("occurred_at must be timezone-aware")


@dataclass(frozen=True, slots=True)
class EventDispatchResult:
    event_id: str
    handled: int
    errors: tuple[AppError, ...]


class EventRouter:
    """Routes validated internal events to subscribed handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if not event_type.strip():
            raise ValidationError("event_type must not be empty")
        if handler in self._handlers[event_type]:
            return
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> bool:
        handlers = self._handlers.get(event_type, [])
        if handler not in handlers:
            return False
        handlers.remove(handler)
        return True

    async def dispatch(self, event: EventEnvelope) -> EventDispatchResult:
        handlers = tuple(self._handlers.get(event.event_type, ()))
        errors: list[AppError] = []
        handled = 0

        for handler in handlers:
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    await result
                handled += 1
            except Exception as exc:
                errors.append(classify_error(exc))

        return EventDispatchResult(
            event_id=event.event_id,
            handled=handled,
            errors=tuple(errors),
        )
