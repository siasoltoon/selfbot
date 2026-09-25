import asyncio

from selfbot.db import Database
from selfbot.domain_store import DomainStore
from selfbot.capabilities import CapabilityService
from selfbot.events import EventEnvelope, EventRouter
from selfbot.runtime_router import TelegramRuntimeRouter


class FakeTelegram:
    def __init__(self):
        self.events = EventRouter()
        self.sent = []
        self.panels = []

    async def send_message(self, chat_id, text, *, account_id=None):
        self.sent.append((chat_id, text, account_id))

    async def open_panel(self, chat_id, *, owner_id, account_id=None):
        self.panels.append((chat_id, owner_id, account_id))


def test_router_opens_panel_for_outgoing_saved_message_and_group_command():
    db = Database("sqlite+pysqlite:///:memory:")
    db.create_schema_for_tests()
    class Services:
        capabilities = CapabilityService(DomainStore(db))
    telegram = FakeTelegram()
    router = TelegramRuntimeRouter(telegram, None, allow_linked_accounts=True, services=Services())
    router.start()

    async def run():
        for chat_id in ("self", "-100123"):
            await telegram.events.dispatch(EventEnvelope(
                "telegram.new_message",
                "telegram.account.1",
                {"text": "/پنل", "telegram_account_id": "1", "outgoing": True},
                actor_id="owner",
                chat_id=chat_id,
            ))
    asyncio.run(run())

    assert telegram.panels == [("self", "owner", "1"), ("-100123", "owner", "1")]
    db.engine.dispose()


def test_router_ignores_incoming_group_command():
    db = Database("sqlite+pysqlite:///:memory:")
    db.create_schema_for_tests()
    class Services:
        capabilities = CapabilityService(DomainStore(db))
    telegram = FakeTelegram()
    router = TelegramRuntimeRouter(telegram, None, allow_linked_accounts=True, services=Services())
    router.start()

    asyncio.run(telegram.events.dispatch(EventEnvelope(
        "telegram.new_message",
        "telegram.account.1",
        {"text": "/capability ai on", "telegram_account_id": "1", "outgoing": False},
        actor_id="owner",
        chat_id="-100123",
    )))
    assert not telegram.sent
    db.engine.dispose()
