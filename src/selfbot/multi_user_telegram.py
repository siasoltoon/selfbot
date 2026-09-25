"""Secure multi-user Telegram account onboarding and runtime.

The onboarding bot is separate from the user-account clients. Login codes and
2FA passwords are accepted only in the transient onboarding flow and are never
persisted or emitted to the application event bus. Long-lived Telethon sessions
are encrypted at rest.
"""
from __future__ import annotations

import asyncio
import inspect
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Protocol
from uuid import uuid4

from sqlalchemy import select

from .db import Database
from .errors import ConfigurationError, DependencyError, NotFoundError, ValidationError
from .events import EventEnvelope, EventRouter
from .logging import get_logger
from .multi_user_models import TelegramAccount
from .multi_user_security import SessionCipher


class AuthClient(Protocol):
    session: Any
    async def connect(self) -> Any: ...
    async def disconnect(self) -> Any: ...
    async def send_code_request(self, phone: str) -> Any: ...
    async def sign_in(self, phone: str | None = None, code: str | None = None, *, password: str | None = None, phone_code_hash: str | None = None) -> Any: ...
    async def get_me(self) -> Any: ...


@dataclass(slots=True)
class PendingLogin:
    owner_user_id: str
    phone: str
    client: AuthClient
    phone_code_hash: str
    expires_at: float


class TelegramSessionStore:
    """Durable encrypted Telegram session repository."""

    def __init__(self, database: Database, cipher: SessionCipher) -> None:
        self.database = database
        self.cipher = cipher

    def save(self, owner_user_id: str, telegram_account_id: str, session: str) -> str:
        if not owner_user_id.strip() or not telegram_account_id.strip() or not session.strip():
            raise ValidationError("owner_user_id, telegram_account_id and session are required")
        encrypted = self.cipher.encrypt(session)
        now = datetime.now(timezone.utc)
        with self.database.session() as db:
            existing = db.scalar(
                select(TelegramAccount).where(
                    TelegramAccount.owner_user_id == owner_user_id,
                    TelegramAccount.telegram_account_id == telegram_account_id,
                    TelegramAccount.status == "connected",
                )
            )
            if existing:
                existing.encrypted_session = encrypted
                existing.updated_at = now
                return existing.id
            record = TelegramAccount(
                id=str(uuid4()),
                owner_user_id=owner_user_id,
                telegram_account_id=telegram_account_id,
                encrypted_session=encrypted,
                status="connected",
                created_at=now,
                updated_at=now,
            )
            db.add(record)
            return record.id

    def get_connected(self, owner_user_id: str) -> TelegramAccount:
        with self.database.session() as db:
            record = db.scalar(
                select(TelegramAccount).where(
                    TelegramAccount.owner_user_id == owner_user_id,
                    TelegramAccount.status == "connected",
                ).order_by(TelegramAccount.updated_at.desc())
            )
            if record is None:
                raise NotFoundError("no connected Telegram account")
            db.expunge(record)
            return record

    def list_connected(self) -> list[TelegramAccount]:
        with self.database.session() as db:
            records = list(db.scalars(select(TelegramAccount).where(TelegramAccount.status == "connected")))
            for record in records:
                db.expunge(record)
            return records

    def decrypt(self, record: TelegramAccount) -> str:
        return self.cipher.decrypt(record.encrypted_session)

    def revoke(self, owner_user_id: str) -> int:
        now = datetime.now(timezone.utc)
        with self.database.session() as db:
            records = list(db.scalars(select(TelegramAccount).where(
                TelegramAccount.owner_user_id == owner_user_id,
                TelegramAccount.status == "connected",
            )))
            for record in records:
                record.status = "revoked"
                record.updated_at = now
            return len(records)


class TelegramAuthenticationService:
    """Interactive phone/code/2FA login with strictly transient credentials."""

    def __init__(
        self,
        api_id: str,
        api_hash: str,
        store: TelegramSessionStore,
        *,
        client_factory: Callable[[str, int, str], AuthClient] | None = None,
        ttl_seconds: int = 600,
    ) -> None:
        if not api_id or not api_hash:
            raise ConfigurationError("Telegram API credentials are required")
        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.store = store
        self.client_factory = client_factory
        self.ttl_seconds = ttl_seconds
        self._pending: dict[str, PendingLogin] = {}
        self._lock = asyncio.Lock()

    def _new_client(self) -> AuthClient:
        if self.client_factory:
            return self.client_factory("memory", self.api_id, self.api_hash)
        try:
            from telethon import TelegramClient
        except ImportError as exc:
            raise DependencyError("Telethon is not installed", retryable=False) from exc
        return TelegramClient(None, self.api_id, self.api_hash)

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        value = re.sub(r"[\s()-]", "", phone.strip())
        if not re.fullmatch(r"\+[1-9]\d{7,14}", value):
            raise ValidationError("phone must use international format, for example +989123456789")
        return value

    async def _cleanup_expired(self) -> None:
        now = time.monotonic()
        expired = [key for key, item in self._pending.items() if item.expires_at <= now]
        for key in expired:
            item = self._pending.pop(key, None)
            if item:
                await item.client.disconnect()

    async def begin(self, owner_user_id: str, phone: str) -> None:
        phone = self._normalize_phone(phone)
        async with self._lock:
            self._cleanup_expired()
            old = self._pending.pop(owner_user_id, None)
            if old:
                await old.client.disconnect()
            client = self._new_client()
            await client.connect()
            sent = await client.send_code_request(phone)
            code_hash = getattr(sent, "phone_code_hash", None)
            if not code_hash:
                await client.disconnect()
                raise DependencyError("Telegram did not return a phone code hash", retryable=True)
            self._pending[owner_user_id] = PendingLogin(
                owner_user_id=owner_user_id,
                phone=phone,
                client=client,
                phone_code_hash=str(code_hash),
                expires_at=time.monotonic() + self.ttl_seconds,
            )

    async def verify_code(self, owner_user_id: str, code: str) -> str:
        async with self._lock:
            item = await self._get_pending(owner_user_id)
            if not re.fullmatch(r"\d{3,8}", code.strip()):
                raise ValidationError("Telegram login code must contain only digits")
            try:
                await item.client.sign_in(
                    phone=item.phone,
                    code=code.strip(),
                    phone_code_hash=item.phone_code_hash,
                )
            except Exception as exc:
                if exc.__class__.__name__ == "SessionPasswordNeededError":
                    return "2fa_required"
                raise
            return await self._finalize(owner_user_id, item)

    async def verify_2fa(self, owner_user_id: str, password: str) -> str:
        if not password:
            raise ValidationError("2FA password must not be empty")
        async with self._lock:
            item = self._get_pending(owner_user_id)
            try:
                await item.client.sign_in(password=password)
            finally:
                # Never retain the password after this call returns.
                password = ""
            return await self._finalize(owner_user_id, item)

    async def _get_pending(self, owner_user_id: str) -> PendingLogin:
        await self._cleanup_expired()
        item = self._pending.get(owner_user_id)
        if item is None:
            raise NotFoundError("no active Telegram login; start again")
        return item

    async def _finalize(self, owner_user_id: str, item: PendingLogin) -> str:
        me = await item.client.get_me()
        account_id = str(getattr(me, "id", "") or "")
        if not account_id:
            raise DependencyError("Telegram login succeeded but account identity was unavailable", retryable=False)
        session = item.client.session.save()
        self.store.save(owner_user_id, account_id, session)
        self._pending.pop(owner_user_id, None)
        await item.client.disconnect()
        return account_id

    async def cancel(self, owner_user_id: str) -> None:
        async with self._lock:
            item = self._pending.pop(owner_user_id, None)
            if item:
                await item.client.disconnect()

    async def cancel_all(self) -> None:
        async with self._lock:
            items, self._pending = self._pending, {}
            for item in items.values():
                await item.client.disconnect()


class MultiUserTelegramRuntime:
    """Runs every connected user account as an independent Telethon client."""

    def __init__(
        self,
        store: TelegramSessionStore,
        events: EventRouter,
        *,
        client_factory: Callable[[str, int, str], Any] | None = None,
    ) -> None:
        self.store = store
        self.events = events
        self.client_factory = client_factory
        self._clients: dict[str, Any] = {}

    def _new_client(self, session: str, api_id: int, api_hash: str) -> Any:
        if self.client_factory:
            return self.client_factory(session, api_id, api_hash)
        try:
            from telethon import TelegramClient
        except ImportError as exc:
            raise DependencyError("Telethon is not installed", retryable=False) from exc
        return TelegramClient(session, api_id, api_hash)

    async def start(self, api_id: str, api_hash: str) -> None:
        if not api_id or not api_hash:
            raise ConfigurationError("Telegram API credentials are required")
        for record in self.store.list_connected():
            session = self.store.decrypt(record)
            client = self._new_client(session, int(api_id), api_hash)
            try:
                result = client.start()
                if inspect.isawaitable(result):
                    await result
                client.add_event_handler(self._handler(record.owner_user_id, record.telegram_account_id))
                self._clients[record.telegram_account_id] = client
            except Exception:
                result = client.disconnect()
                if inspect.isawaitable(result):
                    await result
                raise

    def _handler(self, owner_user_id: str, account_id: str) -> Callable[[Any], Awaitable[None]]:
        async def handler(event: Any) -> None:
            message = getattr(event, "message", event)
            occurred_at = getattr(message, "date", None) or datetime.now(timezone.utc)
            if occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(tzinfo=timezone.utc)
            await self.events.dispatch(EventEnvelope(
                event_type="telegram.new_message",
                source=f"telegram.account.{account_id}",
                actor_id=owner_user_id,
                chat_id=str(getattr(message, "chat_id", "") or ""),
                occurred_at=occurred_at,
                payload={
                    "message_id": str(getattr(message, "id", "") or ""),
                    "text": getattr(message, "message", None),
                    "telegram_account_id": account_id,
                },
            ))
        return handler

    async def send_message(self, chat_id: str | int, text: str, *, account_id: str | None = None) -> Any:
        if not account_id:
            raise ValidationError("telegram account id is required for multi-user transport")
        client = self._clients.get(account_id)
        if client is None:
            raise NotFoundError("Telegram account runtime is not active")
        if not text.strip():
            raise ValidationError("Telegram message text must not be empty")
        return await client.send_message(chat_id, text)

    async def stop(self) -> None:
        clients, self._clients = self._clients, {}
        for client in clients.values():
            result = client.disconnect()
            if inspect.isawaitable(result):
                await result


class OnboardingBot:
    """Normal Telegram bot used only to install/manage user selfbot sessions."""

    def __init__(
        self,
        token: str,
        api_id: str,
        api_hash: str,
        auth: TelegramAuthenticationService,
        store: TelegramSessionStore,
    ) -> None:
        if not token.strip():
            raise ConfigurationError("TELEGRAM_ONBOARDING_BOT_TOKEN is required")
        self.token = token
        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.auth = auth
        self.store = store
        self._client: Any = None
        self._started = False
        self._states: dict[str, str] = {}
        self.logger = get_logger(__name__)

    async def start(self) -> None:
        if self._started:
            return
        try:
            from telethon import TelegramClient, events
        except ImportError as exc:
            raise DependencyError("Telethon is not installed", retryable=False) from exc
        self._client = TelegramClient(None, self.api_id, self.api_hash)
        await self._client.start(bot_token=self.token)

        @self._client.on(events.NewMessage(incoming=True))
        async def on_message(event: Any) -> None:
            sender = await event.get_sender()
            user_id = str(getattr(sender, "id", "") or "")
            if not user_id:
                return
            text = (getattr(event, "raw_text", "") or "").strip()
            await self._handle(user_id, event, text)

        self._started = True
        self.logger.info("Telegram onboarding bot started")

    async def _handle(self, user_id: str, event: Any, text: str) -> None:
        lower = text.lower()
        if lower in {"/start", "/help"}:
            await event.reply(
                "سلام. برای اتصال سلف‌بات از /connect استفاده کن.\n"
                "در مراحل بعد شماره، کد ورود تلگرام و در صورت فعال بودن، رمز دومرحله‌ای را می‌گیریم.\n"
                "کد و رمز ذخیره یا در لاگ ثبت نمی‌شوند."
            )
            return
        if lower == "/connect":
            self._states[user_id] = "phone"
            await event.reply("شماره اکانت تلگرام را با فرمت بین‌المللی بفرست؛ مثال: +989123456789")
            return
        if lower == "/status":
            try:
                record = self.store.get_connected(user_id)
            except NotFoundError:
                await event.reply("اکانت تلگرام متصل نیست.")
            else:
                await event.reply(f"اکانت متصل است. شناسه داخلی تلگرام: {record.telegram_account_id}")
            return
        if lower == "/disconnect":
            await self.auth.cancel(user_id)
            count = self.store.revoke(user_id)
            self._states.pop(user_id, None)
            await event.reply("اتصال لغو شد." if count == 0 else "اتصال اکانت قطع شد. برای اتصال دوباره /connect را بزن.")
            return

        state = self._states.get(user_id)
        if state == "phone":
            try:
                await self.auth.begin(user_id, text)
            except Exception:
                await event.reply("شماره معتبر نیست یا شروع ورود ناموفق بود. دوباره /connect را بزن.")
                return
            self._states[user_id] = "code"
            await event.reply("کد ورود تلگرام را بفرست. این کد ذخیره نمی‌شود.")
            return
        if state == "code":
            try:
                result = await self.auth.verify_code(user_id, text)
            except Exception:
                await event.reply("کد نامعتبر یا منقضی است. /connect را دوباره اجرا کن.")
                self._states.pop(user_id, None)
                return
            if result == "2fa_required":
                self._states[user_id] = "password"
                await event.reply("رمز دومرحله‌ای تلگرام را بفرست. رمز ذخیره یا لاگ نمی‌شود.")
                return
            self._states.pop(user_id, None)
            await event.reply("اتصال با موفقیت انجام شد.")
            return
        if state == "password":
            try:
                await self.auth.verify_2fa(user_id, text)
            except Exception:
                await event.reply("رمز دومرحله‌ای نامعتبر است یا ورود کامل نشد. /connect را دوباره اجرا کن.")
                self._states.pop(user_id, None)
                return
            self._states.pop(user_id, None)
            await event.reply("اتصال با موفقیت انجام شد.")
            return

    async def stop(self) -> None:
        await self.auth.cancel_all()
        if self._client is not None:
            result = self._client.disconnect()
            if inspect.isawaitable(result):
                await result
        self._client = None
        self._started = False
