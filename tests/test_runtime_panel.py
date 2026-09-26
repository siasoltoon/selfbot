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


def test_onboarding_bot_panel_command_replies_with_real_buttons():
    from selfbot.multi_user_telegram import OnboardingBot
    from selfbot.panel import PanelService

    db = Database("sqlite+pysqlite:///:memory:")
    db.create_schema_for_tests()
    capabilities = CapabilityService(DomainStore(db))

    class FakeStore:
        def get_connected(self, owner_id):
            return object()

    class FakeAuth:
        @staticmethod
        def _owner_fingerprint(owner_id):
            return "fingerprint"

        @staticmethod
        def _safe_exception_message(exc):
            return str(exc)

    class Event:
        def __init__(self):
            self.replies = []

        async def reply(self, text, **kwargs):
            self.replies.append((text, kwargs))

    bot = OnboardingBot.__new__(OnboardingBot)
    bot.auth = FakeAuth()
    bot.store = FakeStore()
    bot.capabilities = capabilities
    bot.panel = PanelService(capabilities)
    bot.panel_token_factory = lambda owner_id: "signed-token"
    bot.logger = type("Logger", (), {"warning": staticmethod(lambda *args, **kwargs: None)})()

    event = Event()
    asyncio.run(bot._handle("owner", event, "/پنل"))

    assert len(event.replies) == 1
    text, kwargs = event.replies[0]
    assert "Selfbot Control Center" in text
    assert sum(len(row) for row in kwargs["buttons"]) >= 6
    db.engine.dispose()


def test_router_supports_balance_and_transfer_commands(tmp_path):
    from selfbot.economy import EconomyService

    db = Database(f"sqlite:///{tmp_path / 'router-economy.db'}")
    db.create_schema_for_tests()
    capabilities = CapabilityService(DomainStore(db))
    capabilities.set_enabled("owner", "panel_diamond_transfer", True)

    class Services:
        capabilities = capabilities
        economy = EconomyService(db, capabilities, owner_id="owner")

    telegram = FakeTelegram()
    router = TelegramRuntimeRouter(telegram, None, allow_linked_accounts=True, services=Services())
    router.start()

    async def run():
        await telegram.events.dispatch(EventEnvelope(
            "telegram.new_message", "telegram.account.1",
            {"text": ".موجودی", "telegram_account_id": "1", "outgoing": True},
            actor_id="owner", chat_id="self",
        ))
        Services.economy.adjust("owner", "owner", 100)
        await telegram.events.dispatch(EventEnvelope(
            "telegram.new_message", "telegram.account.1",
            {"text": ".انتقال 50 200", "telegram_account_id": "1", "outgoing": True},
            actor_id="owner", chat_id="self",
        ))

    asyncio.run(run())
    assert "100" in telegram.sent[0][1]
    assert "انتقال انجام شد" in telegram.sent[1][1]
    assert Services.economy.balance("owner") == 49
    assert Services.economy.balance("200") == 50
    db.engine.dispose()
