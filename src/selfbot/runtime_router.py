"""Runtime routing from Telegram events to safe built-in commands."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from .errors import AuthorizationError, NotFoundError, ValidationError
from .services import CoreServices


class TelegramTransport(Protocol):
    events: object
    async def send_message(self, chat_id: str | int, text: str, *, account_id: str | None = None): ...
    async def open_panel(self, chat_id: str | int, *, owner_id: str, account_id: str | None = None): ...


@dataclass(slots=True)
class TelegramRuntimeRouter:
    telegram: TelegramTransport
    owner_id: str | None
    allow_linked_accounts: bool = False
    services: CoreServices | None = None

    def start(self) -> None:
        self.telegram.events.subscribe("telegram.new_message", self._handle_message)

    async def _send(self, event, text: str) -> None:
        account_id = event.payload.get("telegram_account_id")
        await self.telegram.send_message(
            event.chat_id or event.actor_id,
            text,
            account_id=account_id,
        )

    @staticmethod
    def _command(text: str) -> tuple[str, list[str]]:
        parts = text.split()
        if not parts:
            return "", []
        return parts[0].split("@", 1)[0].lower(), parts[1:]

    async def _handle_message(self, event) -> None:
        if self.owner_id:
            if event.actor_id != self.owner_id:
                return
        elif not self.allow_linked_accounts:
            return

        # Commands are deliberately restricted to messages sent by the connected
        # account itself. This prevents a group member from controlling the owner.
        if not bool(event.payload.get("outgoing", False)):
            return

        text = str(event.payload.get("text") or "").strip()
        if not text.startswith("/"):
            return

        command, args = self._command(text)
        account_id = event.payload.get("telegram_account_id")
        owner_id = str(event.actor_id or self.owner_id or "").strip()

        if command in {"/panel", "/پنل"}:
            try:
                await self.telegram.open_panel(
                    event.chat_id or owner_id,
                    owner_id=owner_id,
                    account_id=account_id,
                )
            except Exception:
                await self._send(
                    event,
                    "پنل تعاملی در دسترس نیست. قابلیت Inline Mode ربات مدیریت را بررسی کن.",
                )
            return

        if command == "/ping":
            await self._send(event, "pong")
            return

        if command == "/status":
            if self.services is None:
                await self._send(event, "Selfbot is running.")
                return
            snapshot = self.services.capabilities.snapshot(owner_id)
            enabled = sum(snapshot.values())
            await self._send(event, f"Selfbot فعال است. قابلیت‌های روشن: {enabled}/{len(snapshot)}")
            return

        if command in {"/capability", "/قابلیت"}:
            if self.services is None:
                await self._send(event, "Capability service is unavailable.")
                return
            if len(args) != 2 or args[1].lower() not in {"on", "off", "روشن", "خاموش"}:
                await self._send(event, "فرمت: /capability <id> on|off")
                return
            capability_id = args[0].strip().lower()
            enabled = args[1].lower() in {"on", "روشن"}
            try:
                self.services.capabilities.set_enabled(owner_id, capability_id, enabled)
            except (ValidationError, NotFoundError) as exc:
                await self._send(event, f"تغییر قابلیت انجام نشد: {exc}")
                return
            state = "روشن" if enabled else "خاموش"
            await self._send(event, f"قابلیت «{capability_id}» {state} شد.")
            return

        if command == "/help":
            await self._send(
                event,
                "دستورات فعال:\n/panel یا /پنل\n/status\n/capability <id> on|off\n/help",
            )
