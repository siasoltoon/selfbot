"""Secure multi-user Telegram account onboarding and runtime.

The onboarding bot is separate from the user-account clients. QR login is the
primary onboarding mechanism because Telegram/Telethon can invalidate a login
code that is sent through the same application. 2FA passwords remain transient
and are never persisted or emitted to the application event bus.
"""
from __future__ import annotations

import asyncio
import hashlib
import inspect
import io
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
    async def is_user_authorized(self) -> bool: ...


class QRAuthClient(AuthClient, Protocol):
    async def qr_login(self, ignored_ids: list[int] | None = None) -> Any: ...


@dataclass(slots=True)
class PendingLogin:
    owner_user_id: str
    phone: str
    client: AuthClient
    phone_code_hash: str
    expires_at: float
    code_requested_at: float
    code_timeout_seconds: int | None = None
    code_type: str | None = None
    next_code_type: str | None = None
    code_attempts: int = 0


@dataclass(slots=True)
class PendingQRLogin:
    owner_user_id: str
    client: QRAuthClient
    qr_login: Any
    expires_at: float
    wait_task: asyncio.Task[Any] | None = None
    two_fa_required: bool = False


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
    """Transient Telegram authentication with QR login as the primary flow."""

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
        self._pending_qr: dict[str, PendingQRLogin] = {}
        self._lock = asyncio.Lock()
        self.logger = get_logger(__name__)

    @staticmethod
    def _mask_phone(phone: str) -> str:
        normalized = re.sub(r"\s+", "", phone)
        if len(normalized) <= 4:
            return "***"
        return f"{normalized[:3]}***{normalized[-2:]}"

    @staticmethod
    def _owner_fingerprint(owner_user_id: str) -> str:
        return hashlib.sha256(owner_user_id.encode("utf-8")).hexdigest()[:12]

    @staticmethod
    def _safe_exception_message(exc: Exception, *, secrets: tuple[str, ...] = ()) -> str:
        message = str(exc).replace("\n", " ")[:500]
        for secret in secrets:
            if secret:
                message = message.replace(secret, "[REDACTED]")
        return message

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

    @staticmethod
    def _qr_png(url: str) -> bytes:
        try:
            import qrcode
        except ImportError as exc:
            raise DependencyError("qrcode is not installed", retryable=False) from exc
        image = qrcode.make(url)
        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()

    async def _cleanup_expired(self) -> None:
        now = time.monotonic()
        expired = [key for key, item in self._pending.items() if item.expires_at <= now]
        for key in expired:
            item = self._pending.pop(key, None)
            if item:
                self.logger.info(
                    "telegram login expired",
                    extra={"context": {
                        "stage": "cleanup_expired",
                        "owner_fingerprint": self._owner_fingerprint(item.owner_user_id),
                        "phone_masked": self._mask_phone(item.phone),
                    }},
                )
                try:
                    await item.client.disconnect()
                except Exception as exc:
                    self.logger.warning(
                        "telegram login client cleanup failed",
                        extra={"context": {
                            "stage": "cleanup_expired_disconnect",
                            "owner_fingerprint": self._owner_fingerprint(item.owner_user_id),
                            "exception_type": type(exc).__name__,
                            "exception_module": type(exc).__module__,
                            "error_message": self._safe_exception_message(exc),
                        }},
                    )

        expired_qr = [key for key, item in self._pending_qr.items() if item.expires_at <= now]
        for key in expired_qr:
            item = self._pending_qr.pop(key, None)
            if item:
                if item.wait_task and not item.wait_task.done():
                    item.wait_task.cancel()
                try:
                    await item.client.disconnect()
                except Exception as exc:
                    self.logger.warning(
                        "telegram qr login client cleanup failed",
                        extra={"context": {
                            "stage": "cleanup_expired_qr_disconnect",
                            "owner_fingerprint": self._owner_fingerprint(item.owner_user_id),
                            "exception_type": type(exc).__name__,
                            "exception_module": type(exc).__module__,
                            "error_message": self._safe_exception_message(exc),
                        }},
                    )

    async def begin_qr(self, owner_user_id: str) -> tuple[bytes, int]:
        """Start a transient QR login and return PNG bytes plus TTL seconds."""
        async with self._lock:
            await self._cleanup_expired()
            old = self._pending.pop(owner_user_id, None)
            if old:
                await old.client.disconnect()
            old_qr = self._pending_qr.pop(owner_user_id, None)
            if old_qr:
                if old_qr.wait_task and not old_qr.wait_task.done():
                    old_qr.wait_task.cancel()
                await old_qr.client.disconnect()

            client = self._new_client()
            started = time.monotonic()
            self.logger.info(
                "telegram qr login started",
                extra={"context": {
                    "stage": "qr_begin",
                    "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                    "ttl_seconds": self.ttl_seconds,
                }},
            )
            try:
                await client.connect()
                ignored_ids: list[int] = []
                for record in self.store.list_connected():
                    try:
                        ignored_ids.append(int(record.telegram_account_id))
                    except ValueError:
                        continue
                qr_login = await client.qr_login(ignored_ids=ignored_ids)
                expires = getattr(qr_login, "expires", None)
                if not isinstance(expires, datetime):
                    raise DependencyError("Telegram did not return a QR expiry", retryable=True)
                expires_utc = expires.astimezone(timezone.utc) if expires.tzinfo else expires.replace(tzinfo=timezone.utc)
                ttl = max(1, min(self.ttl_seconds, int((expires_utc - datetime.now(timezone.utc)).total_seconds())))
                item = PendingQRLogin(
                    owner_user_id=owner_user_id,
                    client=client,
                    qr_login=qr_login,
                    expires_at=time.monotonic() + ttl,
                )
                self._pending_qr[owner_user_id] = item
                item.wait_task = asyncio.create_task(self._wait_for_qr(owner_user_id, item))
                png = self._qr_png(str(qr_login.url))
            except Exception as exc:
                self.logger.error(
                    "telegram qr login start failed",
                    extra={"context": {
                        "stage": "qr_begin",
                        "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                        "elapsed_ms": round((time.monotonic() - started) * 1000),
                        "exception_type": type(exc).__name__,
                        "exception_module": type(exc).__module__,
                        "error_message": self._safe_exception_message(exc),
                    }},
                    exc_info=True,
                )
                failed_item = self._pending_qr.pop(owner_user_id, None)
                if failed_item and failed_item.wait_task and not failed_item.wait_task.done():
                    failed_item.wait_task.cancel()
                try:
                    await client.disconnect()
                except Exception:
                    pass
                raise
            self.logger.info(
                "telegram qr login challenge created",
                extra={"context": {
                    "stage": "qr_begin",
                    "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                    "elapsed_ms": round((time.monotonic() - started) * 1000),
                    "qr_ttl_seconds": ttl,
                }},
            )
            return png, ttl

    async def _wait_for_qr(self, owner_user_id: str, item: PendingQRLogin) -> str:
        timeout = max(1, item.expires_at - time.monotonic())
        try:
            await item.qr_login.wait(timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.info(
                "telegram qr login expired",
                extra={"context": {
                    "stage": "qr_wait",
                    "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                    "reason": "timeout",
                }},
            )
            self._pending_qr.pop(owner_user_id, None)
            await item.client.disconnect()
            return "expired"
        except Exception as exc:
            if exc.__class__.__name__ == "SessionPasswordNeededError":
                item.two_fa_required = True
                # The QR itself may expire immediately after scanning. Keep the
                # authenticated transient client alive for the separate 2FA step.
                item.expires_at = time.monotonic() + self.ttl_seconds
                self.logger.info(
                    "telegram qr login accepted; 2fa required",
                    extra={"context": {
                        "stage": "qr_wait",
                        "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                        "exception_type": type(exc).__name__,
                    }},
                )
                return "2fa_required"
            self.logger.error(
                "telegram qr login failed",
                extra={"context": {
                    "stage": "qr_wait",
                    "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                    "exception_type": type(exc).__name__,
                    "exception_module": type(exc).__module__,
                    "error_message": self._safe_exception_message(exc),
                }},
                exc_info=True,
            )
            self._pending_qr.pop(owner_user_id, None)
            try:
                await item.client.disconnect()
            except Exception:
                pass
            return "failed"
        try:
            await self._finalize_client(owner_user_id, item.client)
        except Exception as exc:
            self.logger.error(
                "telegram qr login finalization failed",
                extra={"context": {
                    "stage": "qr_finalize",
                    "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                    "exception_type": type(exc).__name__,
                    "exception_module": type(exc).__module__,
                    "error_message": self._safe_exception_message(exc),
                }},
                exc_info=True,
            )
            self._pending_qr.pop(owner_user_id, None)
            try:
                await item.client.disconnect()
            except Exception:
                pass
            return "failed"
        self.logger.info(
            "telegram qr login finalized successfully",
            extra={"context": {
                "stage": "qr_finalize",
                "owner_fingerprint": self._owner_fingerprint(owner_user_id),
            }},
        )
        self._pending_qr.pop(owner_user_id, None)
        return "connected"

    async def verify_qr_2fa(self, owner_user_id: str, password: str) -> str:
        if not password:
            raise ValidationError("2FA password must not be empty")
        async with self._lock:
            await self._cleanup_expired()
            item = self._pending_qr.get(owner_user_id)
            if item is None or not item.two_fa_required:
                raise NotFoundError("no Telegram QR login requires 2FA")
            started = time.monotonic()
            try:
                await item.client.sign_in(password=password)
                account_id = await self._finalize_client(owner_user_id, item.client)
                self._pending_qr.pop(owner_user_id, None)
            except Exception as exc:
                self.logger.error(
                    "telegram qr 2fa verification failed",
                    extra={"context": {
                        "stage": "qr_verify_2fa",
                        "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                        "elapsed_ms": round((time.monotonic() - started) * 1000),
                        "exception_type": type(exc).__name__,
                        "exception_module": type(exc).__module__,
                        "error_message": self._safe_exception_message(exc),
                    }},
                    exc_info=True,
                )
                raise
            finally:
                password = ""
            return account_id

    async def begin(self, owner_user_id: str, phone: str) -> None:
        """Legacy phone/code API retained for compatibility; onboarding no longer uses it."""
        phone = self._normalize_phone(phone)
        async with self._lock:
            await self._cleanup_expired()
            old = self._pending.pop(owner_user_id, None)
            if old:
                await old.client.disconnect()
            client = self._new_client()
            started = time.monotonic()
            self.logger.info(
                "telegram login started",
                extra={"context": {
                    "stage": "begin",
                    "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                    "phone_masked": self._mask_phone(phone),
                    "ttl_seconds": self.ttl_seconds,
                }},
            )
            try:
                await client.connect()
                sent = await client.send_code_request(phone)
            except Exception as exc:
                self.logger.error(
                    "telegram login code request failed",
                    extra={"context": {
                        "stage": "send_code_request",
                        "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                        "phone_masked": self._mask_phone(phone),
                        "elapsed_ms": round((time.monotonic() - started) * 1000),
                        "exception_type": type(exc).__name__,
                        "exception_module": type(exc).__module__,
                        "error_message": self._safe_exception_message(exc, secrets=(phone,)),
                    }},
                    exc_info=True,
                )
                try:
                    await client.disconnect()
                except Exception:
                    pass
                raise
            code_hash = getattr(sent, "phone_code_hash", None)
            if not code_hash:
                await client.disconnect()
                raise DependencyError("Telegram did not return a phone code hash", retryable=True)
            now = time.monotonic()
            telegram_timeout = getattr(sent, "timeout", None)
            try:
                telegram_timeout = int(telegram_timeout) if telegram_timeout is not None else None
            except (TypeError, ValueError):
                telegram_timeout = None
            sent_type = getattr(getattr(sent, "type", None), "__class__", type(None)).__name__ or None
            next_type = getattr(getattr(sent, "next_type", None), "__class__", type(None)).__name__ or None
            self._pending[owner_user_id] = PendingLogin(
                owner_user_id=owner_user_id,
                phone=phone,
                client=client,
                phone_code_hash=str(code_hash),
                expires_at=now + self.ttl_seconds,
                code_requested_at=now,
                code_timeout_seconds=telegram_timeout,
                code_type=sent_type,
                next_code_type=next_type,
            )
            self.logger.info(
                "telegram login code request succeeded",
                extra={"context": {
                    "stage": "send_code_request",
                    "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                    "phone_masked": self._mask_phone(phone),
                    "elapsed_ms": round((time.monotonic() - started) * 1000),
                    "pending_ttl_seconds": self.ttl_seconds,
                    "telegram_code_timeout_seconds": telegram_timeout,
                    "telegram_code_type": sent_type,
                    "telegram_next_code_type": next_type,
                }},
            )

    async def resend_code(self, owner_user_id: str) -> None:
        """Compatibility recovery for callers still using the legacy phone flow."""
        async with self._lock:
            item = await self._get_pending(owner_user_id)
            started = time.monotonic()
            try:
                sent = await item.client.send_code_request(item.phone)
            except Exception as exc:
                self.logger.error(
                    "telegram login code resend failed",
                    extra={"context": {
                        "stage": "resend_code",
                        "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                        "phone_masked": self._mask_phone(item.phone),
                        "elapsed_ms": round((time.monotonic() - started) * 1000),
                        "exception_type": type(exc).__name__,
                        "exception_module": type(exc).__module__,
                        "error_message": self._safe_exception_message(exc, secrets=(item.phone,)),
                    }},
                    exc_info=True,
                )
                raise
            code_hash = getattr(sent, "phone_code_hash", None)
            if not code_hash:
                raise DependencyError("Telegram did not return a phone code hash for resend", retryable=True)
            item.phone_code_hash = str(code_hash)
            now = time.monotonic()
            item.code_requested_at = now
            item.expires_at = now + self.ttl_seconds
            telegram_timeout = getattr(sent, "timeout", None)
            try:
                telegram_timeout = int(telegram_timeout) if telegram_timeout is not None else None
            except (TypeError, ValueError):
                telegram_timeout = None
            item.code_timeout_seconds = telegram_timeout
            item.code_type = getattr(getattr(sent, "type", None), "__class__", type(None)).__name__ or None
            item.next_code_type = getattr(getattr(sent, "next_type", None), "__class__", type(None)).__name__ or None
            item.code_attempts = 0
            self.logger.info(
                "telegram login code resent",
                extra={"context": {
                    "stage": "resend_code",
                    "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                    "phone_masked": self._mask_phone(item.phone),
                    "elapsed_ms": round((time.monotonic() - started) * 1000),
                    "telegram_code_timeout_seconds": telegram_timeout,
                    "telegram_code_type": item.code_type,
                    "telegram_next_code_type": item.next_code_type,
                }},
            )

    async def verify_code(self, owner_user_id: str, code: str) -> str:
        async with self._lock:
            item = await self._get_pending(owner_user_id)
            normalized_code = code.strip()
            if not re.fullmatch(r"\d{3,8}", normalized_code):
                raise ValidationError("Telegram login code must contain only digits")
            item.code_attempts += 1
            try:
                await item.client.sign_in(
                    phone=item.phone,
                    code=normalized_code,
                    phone_code_hash=item.phone_code_hash,
                )
            except Exception as exc:
                if exc.__class__.__name__ == "SessionPasswordNeededError":
                    return "2fa_required"
                self.logger.error(
                    "telegram login code verification failed",
                    extra={"context": {
                        "stage": "verify_code",
                        "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                        "phone_masked": self._mask_phone(item.phone),
                        "exception_type": type(exc).__name__,
                        "exception_module": type(exc).__module__,
                        "error_message": self._safe_exception_message(exc, secrets=(normalized_code, item.phone)),
                    }},
                    exc_info=True,
                )
                raise
            return await self._finalize(owner_user_id, item)

    async def verify_2fa(self, owner_user_id: str, password: str) -> str:
        if not password:
            raise ValidationError("2FA password must not be empty")
        async with self._lock:
            item = await self._get_pending(owner_user_id)
            try:
                await item.client.sign_in(password=password)
            except Exception as exc:
                self.logger.error(
                    "telegram 2fa verification failed",
                    extra={"context": {
                        "stage": "verify_2fa",
                        "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                        "phone_masked": self._mask_phone(item.phone),
                        "exception_type": type(exc).__name__,
                        "exception_module": type(exc).__module__,
                        "error_message": self._safe_exception_message(exc),
                    }},
                    exc_info=True,
                )
                raise
            finally:
                password = ""
            return await self._finalize(owner_user_id, item)

    async def _get_pending(self, owner_user_id: str) -> PendingLogin:
        await self._cleanup_expired()
        item = self._pending.get(owner_user_id)
        if item is None:
            raise NotFoundError("no active Telegram login; start again")
        return item

    async def _finalize_client(self, owner_user_id: str, client: AuthClient) -> str:
        me = await client.get_me()
        account_id = str(getattr(me, "id", "") or "")
        if not account_id:
            raise DependencyError("Telegram login succeeded but account identity was unavailable", retryable=False)
        session = client.session.save()
        self.store.save(owner_user_id, account_id, session)
        await client.disconnect()
        return account_id

    async def _finalize(self, owner_user_id: str, item: PendingLogin) -> str:
        try:
            account_id = await self._finalize_client(owner_user_id, item.client)
        finally:
            self._pending.pop(owner_user_id, None)
        self.logger.info(
            "telegram login finalized successfully",
            extra={"context": {
                "stage": "finalize",
                "owner_fingerprint": self._owner_fingerprint(owner_user_id),
                "phone_masked": self._mask_phone(item.phone),
                "account_id": account_id,
            }},
        )
        return account_id

    async def cancel(self, owner_user_id: str) -> None:
        async with self._lock:
            item = self._pending.pop(owner_user_id, None)
            if item:
                await item.client.disconnect()
            qr_item = self._pending_qr.pop(owner_user_id, None)
            if qr_item:
                if qr_item.wait_task and not qr_item.wait_task.done():
                    qr_item.wait_task.cancel()
                await qr_item.client.disconnect()

    async def cancel_all(self) -> None:
        async with self._lock:
            items, self._pending = self._pending, {}
            for item in items.values():
                await item.client.disconnect()
            qr_items, self._pending_qr = self._pending_qr, {}
            for item in qr_items.values():
                if item.wait_task and not item.wait_task.done():
                    item.wait_task.cancel()
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
                result = client.connect()
                if inspect.isawaitable(result):
                    await result
                authorized = client.is_user_authorized()
                if inspect.isawaitable(authorized):
                    authorized = await authorized
                if not authorized:
                    raise DependencyError("stored account is not authorized", retryable=False)
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
        self._qr_messages: dict[str, Any] = {}
        self._qr_watchers: dict[str, asyncio.Task[Any]] = {}
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

    async def _watch_qr(self, user_id: str, event: Any) -> None:
        try:
            item = self.auth._pending_qr.get(user_id)
            if item is None or item.wait_task is None:
                return
            result = await item.wait_task
            qr_message = self._qr_messages.pop(user_id, None)
            if qr_message is not None and hasattr(qr_message, "delete"):
                try:
                    await qr_message.delete()
                except Exception:
                    pass
            if result == "connected":
                self._states.pop(user_id, None)
                await event.reply("اتصال با موفقیت انجام شد.")
            elif result == "2fa_required":
                self._states[user_id] = "qr_password"
                await event.reply("QR تأیید شد. رمز دومرحله‌ای تلگرام را بفرست. رمز ذخیره یا لاگ نمی‌شود.")
            elif result == "expired":
                self._states.pop(user_id, None)
                await event.reply("QR منقضی شد. دوباره /connect را بزن.")
            else:
                self._states.pop(user_id, None)
                await event.reply("ورود با QR ناموفق بود. دوباره /connect را بزن.")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self.logger.error(
                "telegram onboarding qr watcher failed",
                extra={"context": {
                    "stage": "qr_watcher",
                    "owner_fingerprint": self.auth._owner_fingerprint(user_id),
                    "exception_type": type(exc).__name__,
                    "exception_module": type(exc).__module__,
                    "error_message": self.auth._safe_exception_message(exc),
                }},
                exc_info=True,
            )
            self._states.pop(user_id, None)
            await event.reply("پردازش QR ناموفق شد. دوباره /connect را بزن.")
        finally:
            self._qr_watchers.pop(user_id, None)

    async def _handle(self, user_id: str, event: Any, text: str) -> None:
        lower = text.lower()
        if lower in {"/start", "/help"}:
            await event.reply(
                "سلام. برای اتصال سلف‌بات از /connect استفاده کن.\n"
                "ورود با QR انجام می‌شود و دیگر کد ورود تلگرام را داخل این چت نمی‌گیریم.\n"
                "QR را باید با یک دستگاه دیگری که قبلاً به همان اکانت تلگرام وارد شده اسکن کنی.\n"
                "در صورت فعال بودن، فقط رمز دومرحله‌ای به‌صورت موقت دریافت می‌شود."
            )
            return
        if lower == "/connect":
            self._states[user_id] = "qr"
            try:
                png, ttl = await self.auth.begin_qr(user_id)
                sent = await event.reply(
                    f"QR ورود تلگرام آماده است. آن را با دستگاه دیگری که به همان اکانت وارد است اسکن کن.\n"
                    f"این QR حدود {ttl} ثانیه اعتبار دارد؛ آن را فوروارد یا ذخیره نکن.",
                    file=io.BytesIO(png),
                )
                self._qr_messages[user_id] = sent
                watcher = asyncio.create_task(self._watch_qr(user_id, event))
                self._qr_watchers[user_id] = watcher
            except Exception:
                self._states.pop(user_id, None)
                await event.reply("ساخت QR ورود ناموفق بود. چند لحظه بعد دوباره /connect را بزن.")
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
            watcher = self._qr_watchers.pop(user_id, None)
            if watcher and not watcher.done():
                watcher.cancel()
            await self.auth.cancel(user_id)
            count = self.store.revoke(user_id)
            self._states.pop(user_id, None)
            await event.reply("اتصال لغو شد." if count == 0 else "اتصال اکانت قطع شد. برای اتصال دوباره /connect را بزن.")
            return
        if self._states.get(user_id) == "qr_password":
            try:
                account_id = await self.auth.verify_qr_2fa(user_id, text)
            except Exception:
                await event.reply("رمز دومرحله‌ای نامعتبر است یا ورود کامل نشد. /connect را دوباره اجرا کن.")
                self._states.pop(user_id, None)
                return
            self._states.pop(user_id, None)
            await event.reply(f"اتصال با موفقیت انجام شد. شناسه داخلی تلگرام: {account_id}")
            return
        if self._states.get(user_id) == "qr":
            if lower == "/resend":
                await event.reply("در روش QR نیازی به /resend نیست؛ اگر QR منقضی شد /connect را دوباره بزن.")
            else:
                await event.reply("QR در حال انتظار برای اسکن است. آن را با یک دستگاه دیگر اسکن کن یا /connect را دوباره بزن.")
            return

    async def stop(self) -> None:
        for task in self._qr_watchers.values():
            if not task.done():
                task.cancel()
        self._qr_watchers.clear()
        await self.auth.cancel_all()
        if self._client is not None:
            result = self._client.disconnect()
            if inspect.isawaitable(result):
                await result
        self._client = None
        self._started = False
