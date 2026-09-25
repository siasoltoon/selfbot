import asyncio
from dataclasses import dataclass

import pytest

from selfbot.db import Database
from selfbot.errors import NotFoundError, ValidationError
from selfbot.multi_user_security import SessionCipher
from selfbot.multi_user_telegram import TelegramAuthenticationService, TelegramSessionStore


class FakeSession:
    def __init__(self):
        self.saved = "encrypted-target-session-source"

    def save(self):
        return self.saved


@dataclass
class SentCode:
    phone_code_hash: str = "hash-123"


@dataclass
class FakeUser:
    id: int = 123456


class FakeClient:
    def __init__(self, require_2fa=False):
        self.session = FakeSession()
        self.require_2fa = require_2fa
        self.connected = False
        self.disconnected = False
        self.received_password = None

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.disconnected = True

    async def send_code_request(self, phone):
        self.phone = phone
        return SentCode()

    async def sign_in(self, phone=None, code=None, *, password=None, phone_code_hash=None):
        if password is not None:
            self.received_password = password
            return FakeUser()
        if self.require_2fa:
            raise type("SessionPasswordNeededError", (Exception,), {})()
        return FakeUser()

    async def get_me(self):
        return FakeUser()


def make_store():
    db = Database("sqlite:///:memory:")
    db.create_schema_for_tests()
    return db, TelegramSessionStore(db, SessionCipher(
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    ))


def test_session_cipher_round_trip():
    cipher = SessionCipher("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    token = cipher.encrypt("telethon-session")
    assert token != "telethon-session"
    assert cipher.decrypt(token) == "telethon-session"
    with pytest.raises(ValidationError):
        cipher.decrypt("not-a-valid-token")


def test_session_store_encrypts_and_revokes():
    db, store = make_store()
    record_id = store.save("owner-1", "123456", "session-secret")
    record = store.get_connected("owner-1")
    assert record.id == record_id
    assert record.encrypted_session != "session-secret"
    assert store.decrypt(record) == "session-secret"
    assert store.revoke("owner-1") == 1
    with pytest.raises(NotFoundError):
        store.get_connected("owner-1")


def test_authentication_finishes_without_persisting_code_or_password():
    db, store = make_store()
    clients = []

    def factory(session, api_id, api_hash):
        client = FakeClient(require_2fa=True)
        clients.append(client)
        return client

    auth = TelegramAuthenticationService("12345", "hash", store, client_factory=factory)

    async def run():
        await auth.begin("owner-1", "+989123456789")
        assert await auth.verify_code("owner-1", "12345") == "2fa_required"
        account_id = await auth.verify_2fa("owner-1", "secret-password")
        return account_id

    assert asyncio.run(run()) == "123456"
    record = store.get_connected("owner-1")
    assert store.decrypt(record) == "encrypted-target-session-source"
    assert clients[0].disconnected is True
    assert clients[0].received_password == "secret-password"
    assert not auth._pending


def test_authentication_logs_safe_telegram_error_details(caplog):
    db, store = make_store()

    class CodeErrorClient(FakeClient):
        async def sign_in(self, phone=None, code=None, *, password=None, phone_code_hash=None):
            if password is None:
                raise type("PhoneCodeInvalidError", (Exception,), {})("code 12345 rejected for +989123456789")

    auth = TelegramAuthenticationService(
        "12345",
        "hash",
        store,
        client_factory=lambda *_: CodeErrorClient(),
    )

    async def run():
        await auth.begin("owner-1", "+989123456789")
        with pytest.raises(Exception) as exc_info:
            await auth.verify_code("owner-1", "12345")
        return exc_info.value

    caplog.set_level("ERROR", logger="selfbot.multi_user_telegram")
    error = asyncio.run(run())

    assert type(error).__name__ == "PhoneCodeInvalidError"
    records = [record for record in caplog.records if record.message == "telegram login code verification failed"]
    assert len(records) == 1
    context = records[0].context
    assert context["stage"] == "verify_code"
    assert context["exception_type"] == "PhoneCodeInvalidError"
    assert context["phone_masked"] == "+98***89"
    assert "12345" not in context["error_message"]
    assert "+989123456789" not in context["error_message"]


def test_authentication_can_resend_after_expired_code():
    db, store = make_store()
    clients = []

    class ExpiringClient(FakeClient):
        def __init__(self, expires=False):
            super().__init__()
            self.expires = expires
            self.sign_in_attempts = 0

        async def sign_in(self, phone=None, code=None, *, password=None, phone_code_hash=None):
            self.sign_in_attempts += 1
            if self.expires:
                raise type("PhoneCodeExpiredError", (Exception,), {})("The confirmation code has expired")
            assert phone_code_hash == "hash-123"
            return FakeUser()

    def factory(*_):
        client = ExpiringClient(expires=not clients)
        clients.append(client)
        return client

    auth = TelegramAuthenticationService("12345", "hash", store, client_factory=factory)

    async def run():
        await auth.begin("owner-1", "+989123456789")
        with pytest.raises(Exception) as exc_info:
            await auth.verify_code("owner-1", "12345")
        assert type(exc_info.value).__name__ == "PhoneCodeExpiredError"
        await auth.resend_code("owner-1")
        return await auth.verify_code("owner-1", "67890")

    assert asyncio.run(run()) == "123456"
    assert len(clients) == 2
    assert clients[0].disconnected is True
    assert clients[1].disconnected is True
    assert not auth._pending


def test_authentication_rejects_bad_phone():
    db, store = make_store()
    auth = TelegramAuthenticationService("12345", "hash", store, client_factory=lambda *_: FakeClient())
    with pytest.raises(ValidationError):
        asyncio.run(auth.begin("owner-1", "09123456789"))
