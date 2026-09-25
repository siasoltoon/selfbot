import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest

from selfbot.db import Database
from selfbot.errors import NotFoundError
from selfbot.multi_user_security import SessionCipher
from selfbot.multi_user_telegram import TelegramAuthenticationService, TelegramSessionStore


@dataclass
class FakeUser:
    id: int = 654321


class FakeSession:
    def save(self):
        return "qr-session-secret"


class FakeQR:
    def __init__(self, *, require_2fa: bool = False):
        self.url = "tg://login?token=test-token"
        self.expires = datetime.now(timezone.utc) + timedelta(seconds=60)
        self.require_2fa = require_2fa

    async def wait(self, timeout=None):
        if self.require_2fa:
            raise type("SessionPasswordNeededError", (Exception,), {})()
        return FakeUser()


class FakeQRClient:
    def __init__(self, *, require_2fa=False):
        self.session = FakeSession()
        self.qr = FakeQR(require_2fa=require_2fa)
        self.connected = False
        self.disconnected = False
        self.ignored_ids = None
        self.password = None

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.disconnected = True

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
        client = FakeQRClient(require_2fa=True)
        clients.append(client)
        return client

    auth = TelegramAuthenticationService("12345", "hash", store, client_factory=factory)

    async def run():
        await auth.begin_qr("owner-1")
        assert await auth._pending_qr["owner-1"].wait_task == "2fa_required"
        return await auth.verify_qr_2fa("owner-1", "secret-password")

    assert asyncio.run(run()) == "654321"
    assert clients[0].password == "secret-password"
    assert clients[0].disconnected is True
    assert store.get_connected("owner-1").telegram_account_id == "654321"


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
