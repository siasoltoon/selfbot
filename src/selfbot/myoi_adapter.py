"""Telegram adapter for the real Myoi game bot.

This layer deliberately does not invent callback-data/API contracts. It interacts
with the real Telegram bot through message text and visible inline-button labels.
Specific game workflows are composed on top after their observed Telegram
behavior is captured and verified.
"""
from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any

from .errors import DependencyError, NotFoundError, ValidationError

@dataclass(frozen=True, slots=True)
class MyoiButton:
    text: str
    row: int
    column: int

@dataclass(frozen=True, slots=True)
class MyoiMessage:
    message_id: int
    text: str
    buttons: tuple[MyoiButton, ...]

class MyoiTelegramAdapter:
    """Provider-neutral boundary for @MeowieeeQBot via a linked user client."""

    BOT_USERNAME = "MeowieeeQBot"

    def __init__(self, client: Any, *, bot_username: str = BOT_USERNAME) -> None:
        self.client = client
        username = str(bot_username).strip().lstrip("@")
        if not username:
            raise ValidationError("Myoi bot username is required")
        self.bot_username = username

    async def _entity(self) -> Any:
        try:
            return await self.client.get_entity(self.bot_username)
        except Exception as exc:
            raise NotFoundError("Myoi bot could not be resolved") from exc

    @staticmethod
    def _button_text(button: Any) -> str:
        return str(getattr(button, "text", "") or "").strip()

    @classmethod
    def _message_view(cls, message: Any) -> MyoiMessage:
        buttons: list[MyoiButton] = []
        matrix = getattr(message, "buttons", None) or []
        for row_index, row in enumerate(matrix):
            for column_index, button in enumerate(row):
                text = cls._button_text(button)
                if text:
                    buttons.append(MyoiButton(text, row_index, column_index))
        return MyoiMessage(
            message_id=int(getattr(message, "id", 0) or 0),
            text=str(getattr(message, "raw_text", None) or getattr(message, "message", None) or ""),
            buttons=tuple(buttons),
        )

    async def send_command(self, command: str, *, chat: Any | None = None) -> Any:
        value = str(command).strip()
        if not value:
            raise ValidationError("Myoi command must not be empty")
        entity = chat if chat is not None else await self._entity()
        try:
            return await self.client.send_message(entity, value)
        except Exception as exc:
            raise DependencyError("Myoi command could not be sent", retryable=True) from exc

    async def recent_messages(self, *, chat: Any | None = None, limit: int = 10) -> tuple[MyoiMessage, ...]:
        if not 1 <= limit <= 50:
            raise ValidationError("Myoi message limit must be between 1 and 50")
        entity = chat if chat is not None else await self._entity()
        try:
            messages = await self.client.get_messages(entity, limit=limit)
        except Exception as exc:
            raise DependencyError("Myoi messages could not be read", retryable=True) from exc
        return tuple(self._message_view(message) for message in messages)

    async def find_button(self, label: str, *, chat: Any | None = None, limit: int = 10) -> tuple[Any, MyoiButton]:
        wanted = str(label).strip()
        if not wanted:
            raise ValidationError("button label is required")
        entity = chat if chat is not None else await self._entity()
        try:
            messages = await self.client.get_messages(entity, limit=limit)
        except Exception as exc:
            raise DependencyError("Myoi messages could not be read", retryable=True) from exc
        for message in messages:
            matrix = getattr(message, "buttons", None) or []
            for row_index, row in enumerate(matrix):
                for column_index, button in enumerate(row):
                    if self._button_text(button) == wanted:
                        return message, MyoiButton(wanted, row_index, column_index)
        raise NotFoundError(f"Myoi button not found: {wanted}")

    async def click_button(self, label: str, *, chat: Any | None = None, limit: int = 10) -> Any:
        message, button = await self.find_button(label, chat=chat, limit=limit)
        matrix = getattr(message, "buttons", None) or []
        try:
            result = matrix[button.row][button.column].click()
            return await result if inspect.isawaitable(result) else result
        except Exception as exc:
            raise DependencyError("Myoi button click failed", retryable=True) from exc

    async def probe(self, *, chat: Any | None = None, limit: int = 10) -> tuple[MyoiMessage, ...]:
        """Read-only observation used before implementing a workflow."""
        return await self.recent_messages(chat=chat, limit=limit)
