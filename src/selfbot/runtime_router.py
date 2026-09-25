"""Runtime routing from Telegram events to safe built-in commands."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import AuthorizationError
from .telegram import TelegramAdapter


@dataclass(slots=True)
class TelegramRuntimeRouter:
    telegram: TelegramAdapter
    owner_id: str | None

    def start(self) -> None:
        self.telegram.events.subscribe("telegram.new_message", self._handle_message)

    async def _handle_message(self, event) -> None:
        if not self.owner_id or event.actor_id != self.owner_id:
            return

        text = str(event.payload.get("text") or "").strip()
        if not text.startswith("/"):
            return

        command = text.split(maxsplit=1)[0].split("@", 1)[0].lower()
        if command == "/ping":
            await self.telegram.send_message(event.chat_id or event.actor_id, "pong", account_id=event.payload.get("telegram_account_id"))
        elif command == "/status":
            await self.telegram.send_message(
                event.chat_id or event.actor_id,
                "Selfbot is running.",
            )
        elif command == "/help":
            await self.telegram.send_message(
                event.chat_id or event.actor_id,
                "دستورات فعال:\n/ping\n/status\n/help",
            )
