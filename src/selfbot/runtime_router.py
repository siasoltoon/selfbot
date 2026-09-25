"""Runtime routing from Telegram events to safe built-in commands."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import AuthorizationError
from typing import Protocol

class TelegramTransport(Protocol):
    events: object
    async def send_message(self, chat_id: str | int, text: str, *, account_id: str | None = None): ...


@dataclass(slots=True)
class TelegramRuntimeRouter:
    telegram: TelegramTransport
    owner_id: str | None
    allow_linked_accounts: bool = False

    def start(self) -> None:
        self.telegram.events.subscribe("telegram.new_message", self._handle_message)

    async def _send(self, event, text: str) -> None:
        account_id = event.payload.get("telegram_account_id")
        if account_id:
            await self.telegram.send_message(event.chat_id or event.actor_id, text, account_id=account_id)
        else:
            await self.telegram.send_message(event.chat_id or event.actor_id, text)

    async def _handle_message(self, event) -> None:
        if self.owner_id:
            if event.actor_id != self.owner_id:
                return
        elif not self.allow_linked_accounts:
            return

        text = str(event.payload.get("text") or "").strip()
        if not text.startswith("/"):
            return

        command = text.split(maxsplit=1)[0].split("@", 1)[0].lower()
        if command == "/ping":
            await self._send(event, "pong")
        elif command == "/status":
            await self._send(event, "Selfbot is running.")
        elif command == "/help":
            await self._send(event, "دستورات فعال:\n/ping\n/status\n/help")
