"""Telegram adapter boundary.

Telegram/Telethon types are confined to this module. Core services consume
normalized application events and a small transport protocol instead.
"""
from __future__ import annotations
import inspect
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol
from .config import Settings
from .errors import ConfigurationError, DependencyError, ValidationError
from .events import EventEnvelope, EventRouter

class TelegramClient(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def send_message(self, chat_id: str | int, text: str) -> Any: ...
    def add_event_handler(self, handler: Callable[[Any], Awaitable[None] | None]) -> None: ...

class TelegramAdapter:
    """Owns Telethon integration and emits normalized internal events."""
    def __init__(self, settings: Settings, events: EventRouter, *, client_factory: Callable[[Settings], TelegramClient] | None = None) -> None:
        self.settings, self.events = settings, events
        self._client_factory = client_factory
        self._client: TelegramClient | None = None
        self._started = False
    @property
    def started(self) -> bool: return self._started
    def _validate_credentials(self) -> None:
        if not self.settings.telegram_api_id or not self.settings.telegram_api_hash:
            raise ConfigurationError("TELEGRAM_API_ID and TELEGRAM_API_HASH are required for Telegram startup")
        try: int(self.settings.telegram_api_id)
        except ValueError as exc: raise ValidationError("TELEGRAM_API_ID must be an integer") from exc
    def _build_client(self) -> TelegramClient:
        if self._client_factory is not None: return self._client_factory(self.settings)
        try:
            from telethon import TelegramClient as TelethonClient
        except ImportError as exc:
            raise DependencyError("Telethon is not installed; Telegram integration is unavailable", retryable=False) from exc
        return TelethonClient(self.settings.telegram_session or "selfbot", int(self.settings.telegram_api_id), self.settings.telegram_api_hash)
    async def start(self) -> None:
        if self._started: return
        self._validate_credentials()
        self._client = self._build_client()
        try:
            result = self._client.start()
            if inspect.isawaitable(result): await result
            self._client.add_event_handler(self._on_new_message)
            self._started = True
        except Exception:
            self._client = None
            raise
    async def stop(self) -> None:
        if not self._started and self._client is None: return
        client, self._client = self._client, None
        self._started = False
        if client is not None:
            result = client.stop()
            if inspect.isawaitable(result): await result
    async def send_message(self, chat_id: str | int, text: str) -> Any:
        if not self._started or self._client is None: raise DependencyError("Telegram client is not started", retryable=False)
        if not text.strip(): raise ValidationError("Telegram message text must not be empty")
        return await self._client.send_message(chat_id, text)
    async def _on_new_message(self, event: Any) -> None:
        message = getattr(event, "message", event)
        occurred_at = getattr(message, "date", None) or datetime.now(timezone.utc)
        if occurred_at.tzinfo is None: occurred_at = occurred_at.replace(tzinfo=timezone.utc)
        chat_id, actor, text_value = getattr(message, "chat_id", None), getattr(message, "sender_id", None), getattr(message, "message", None)
        await self.events.dispatch(EventEnvelope(
            event_type="telegram.new_message", source="telegram",
            actor_id=str(actor) if actor is not None else None,
            chat_id=str(chat_id) if chat_id is not None else None,
            occurred_at=occurred_at,
            payload={"message_id": str(getattr(message, "id", "")), "text": text_value},
        ))
