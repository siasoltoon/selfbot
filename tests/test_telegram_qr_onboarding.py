import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest

from selfbot.db import Database
from selfbot.errors import DependencyError, NotFoundError
from selfbot.multi_user_security import SessionCipher
from selfbot.multi_user_telegram import TelegramAuthenticationService, TelegramSessionStore


@dataclass
class FakeUser:
    id: int = 654321


class FakeSession:
    def save(self):
        return "qr-session-secret"


class FakeQR:
    def __init__(self, *, require_2fa: bool = False, ttl_seconds: int = 60):
        self.url = "tg://login?token=test-token"
        self.expires = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        self.require_2fa = require_2fa

    async def wait(self, timeout=None):
        if self.require_2fa:
            raise type("SessionPasswordNeededError", (Exception,), {})()
        return FakeUser()


class FakeQRClient:
    def __init__(self, *, require_2fa=False, qr_ttl_seconds=60):
        self.session = FakeSession()
        self.qr = FakeQR(require_2fa=require_2fa, ttl_seconds=qr_ttl_seconds)
        self.connected = False
        self.disconnected = False
        self.logged_out = False
        self.ignored_ids = None
        self.password = None

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.disconnected = True

    async def log_out(self):
        self.logged_out = True

    async def qr_login(self, ignored_ids=None):
        self.ignored_ids = ignored_ids
        return self.qr

    async def get_me(self):
        return FakeUser()

    async def sign_in(self, phone=None, code=None, *, password=None, phone_code_hash=None):
        self.password = password
        return FakeUser()


def make_store():
    db = Database("sqlite:///:memory:")
    db.create_schema_for_tests()
    return db, TelegramSessionStore(
        db,
        SessionCipher("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="),
    )


def test_real_telethon_qr_client_uses_persistent_string_session():
    db, store = make_store()
    auth = TelegramAuthenticationService("12345", "hash", store, ttl_seconds=120)
    client = auth._new_client()
    assert client.session.__class__.__name__ == "StringSession"



def test_qr_login_generates_png_and_persists_session():
    db, store = make_store()
    clients = []

    def factory(*_):
        client = FakeQRClient()
        clients.append(client)
        return client

    auth = TelegramAuthenticationService(
        "12345",
        "hash",
        store,
        client_factory=factory,
        ttl_seconds=120,
    )

    async def run():
        png, ttl = await auth.begin_qr("owner-1")
        assert png.startswith(b"\x89PNG\r\n\x1a\n")
        assert ttl > 0
        result = await auth._pending_qr["owner-1"].wait_task
        return result

    assert asyncio.run(run()) == "connected"
    record = store.get_connected("owner-1")
    assert store.decrypt(record) == "qr-session-secret"
    assert clients[0].ignored_ids == []
    assert clients[0].disconnected is True
    assert "owner-1" not in auth._pending_qr


def test_qr_login_requires_2fa_then_finalizes():
    db, store = make_store()
    clients = []

    def factory(*_):
        client = FakeQRClient(require_2fa=True, qr_ttl_seconds=1)
        clients.append(client)
        return client

    auth = TelegramAuthenticationService("12345", "hash", store, client_factory=factory, ttl_seconds=5)

    async def run():
        await auth.begin_qr("owner-1")
        assert await auth._pending_qr["owner-1"].wait_task == "2fa_required"
        assert auth._pending_qr["owner-1"].expires_at - __import__("time").monotonic() > 4
        return await auth.verify_qr_2fa("owner-1", "secret-password")

    assert asyncio.run(run()) == "654321"
    assert clients[0].password == "secret-password"
    assert clients[0].disconnected is True
    assert "owner-1" not in auth._pending_qr
    assert store.get_connected("owner-1").telegram_account_id == "654321"




def test_qr_2fa_persistence_failure_revokes_authenticated_session():
    db, store = make_store()

    def failing_save(owner_user_id, telegram_account_id, session):
        raise RuntimeError("database unavailable")

    store.save = failing_save
    clients = []

    def factory(*_):
        client = FakeQRClient(require_2fa=True, qr_ttl_seconds=1)
        clients.append(client)
        return client

    auth = TelegramAuthenticationService("12345", "hash", store, client_factory=factory, ttl_seconds=5)

    async def run():
        await auth.begin_qr("owner-1")
        assert await auth._pending_qr["owner-1"].wait_task == "2fa_required"
        with pytest.raises(DependencyError, match="durable session storage failed"):
            await auth.verify_qr_2fa("owner-1", "secret-password")

    asyncio.run(run())
    assert clients[0].logged_out is True
    assert clients[0].disconnected is True


def test_qr_login_cancel_disconnects_transient_client():
    db, store = make_store()
    clients = []

    def factory(*_):
        client = FakeQRClient()
        clients.append(client)
        return client

    auth = TelegramAuthenticationService("12345", "hash", store, client_factory=factory)

    async def run():
        await auth.begin_qr("owner-1")
        await auth.cancel("owner-1")

    asyncio.run(run())
    assert clients[0].disconnected is True
    with pytest.raises(NotFoundError):
        store.get_connected("owner-1")
