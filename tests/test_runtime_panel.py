import asyncio

from sqlalchemy.exc import DBAPIError

from selfbot.db import Database, connect_with_retries
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


def test_database_connect_with_retries_only_retries_acquisition():
    class FakeConnection:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    class FakeEngine:
        def __init__(self):
            self.attempts = 0
            self.disposals = 0
            self.connection = FakeConnection()

        def connect(self):
            self.attempts += 1
            if self.attempts < 3:
                raise DBAPIError("connect", {}, RuntimeError("temporary"))
            return self.connection

        def dispose(self):
            self.disposals += 1

    engine = FakeEngine()
    with connect_with_retries(engine, retries=2, retry_delay=0):
        pass

    assert engine.attempts == 3
    assert engine.disposals == 2
    assert engine.connection.closed


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
        def __init__(self):
            self.capabilities = capabilities
            self.economy = EconomyService(db, capabilities, owner_id="owner")
    services = Services()

    telegram = FakeTelegram()
    router = TelegramRuntimeRouter(telegram, None, allow_linked_accounts=True, services=services)
    router.start()

    async def run():
        services.economy.adjust("owner", "owner", 100)
        await telegram.events.dispatch(EventEnvelope(
            "telegram.new_message", "telegram.account.1",
            {"text": ".موجودی", "telegram_account_id": "1", "outgoing": True},
            actor_id="owner", chat_id="self",
        ))
        await telegram.events.dispatch(EventEnvelope(
            "telegram.new_message", "telegram.account.1",
            {"text": ".انتقال 50 200", "telegram_account_id": "1", "outgoing": True},
            actor_id="owner", chat_id="self",
        ))

    asyncio.run(run())
    assert "100" in telegram.sent[0][1]
    assert "انتقال انجام شد" in telegram.sent[1][1]
    assert services.economy.balance("owner") == 49
    assert services.economy.balance("200") == 50
    db.engine.dispose()

def test_real_panel_capabilities_execute_only_when_enabled(tmp_path):
    from types import SimpleNamespace
    from selfbot.tasks import TaskManager

    db = Database(f"sqlite:///{tmp_path / 'panel.db'}")
    db.create_schema_for_tests()
    capabilities = CapabilityService(DomainStore(db))
    services = SimpleNamespace(capabilities=capabilities, tasks=TaskManager(db))
    telegram = FakeTelegram()
    router = TelegramRuntimeRouter(telegram, None, allow_linked_accounts=True, services=services)
    router.start()

    async def dispatch(text):
        await telegram.events.dispatch(EventEnvelope(
            "telegram.new_message", "telegram.account.1",
            {"text": text, "telegram_account_id": "1", "outgoing": True},
            actor_id="owner", chat_id="self",
        ))

    async def run():
        await dispatch(".3 + 5 * 2")
        capabilities.set_enabled("owner", "panel_calculator", True)
        await dispatch(".3 + 5 * 2")
        capabilities.set_enabled("owner", "panel_ping", True)
        await dispatch(".پینگ")
        capabilities.set_enabled("owner", "panel_utility_today", True)
        await dispatch(".امروز")
        capabilities.set_enabled("owner", "panel_utility_id", True)
        await dispatch(".ایدی")

    asyncio.run(run())
    assert "خاموش" in telegram.sent[0][1]
    assert "🧮 13" in telegram.sent[1][1]
    assert "pong" in telegram.sent[2][1]
    assert "📅" in telegram.sent[3][1]
    assert "owner" in telegram.sent[4][1]
    db.engine.dispose()


def test_cancel_capability_cancels_owner_tasks(tmp_path):
    from types import SimpleNamespace
    from selfbot.tasks import TaskManager

    db = Database(f"sqlite:///{tmp_path / 'cancel.db'}")
    db.create_schema_for_tests()
    capabilities = CapabilityService(DomainStore(db))
    capabilities.set_enabled("owner", "panel_utility_cancel", True)
    tasks = TaskManager(db)
    task_id = tasks.create("test", owner_id="owner")
    services = SimpleNamespace(capabilities=capabilities, tasks=tasks)
    telegram = FakeTelegram()
    router = TelegramRuntimeRouter(telegram, None, allow_linked_accounts=True, services=services)
    router.start()

    asyncio.run(telegram.events.dispatch(EventEnvelope(
        "telegram.new_message", "telegram.account.1",
        {"text": ".کنسل", "telegram_account_id": "1", "outgoing": True},
        actor_id="owner", chat_id="self",
    )))
    assert "1 عملیات لغو شد" in telegram.sent[0][1]
    assert tasks.get(task_id).status == "cancelled"
    db.engine.dispose()


def test_database_connection_retry_settings_are_safe():
    from selfbot.config import load_settings
    import os

    original_retries = os.environ.get("DATABASE_CONNECT_RETRIES")
    original_delay = os.environ.get("DATABASE_CONNECT_RETRY_DELAY")
    try:
        os.environ["DATABASE_CONNECT_RETRIES"] = "4"
        os.environ["DATABASE_CONNECT_RETRY_DELAY"] = "0.25"
        settings = load_settings()
        assert settings.database_connect_retries == 4
        assert settings.database_connect_retry_delay == 0.25
        assert settings.database_connect_retries >= 0
    finally:
        if original_retries is None:
            os.environ.pop("DATABASE_CONNECT_RETRIES", None)
        else:
            os.environ["DATABASE_CONNECT_RETRIES"] = original_retries
        if original_delay is None:
            os.environ.pop("DATABASE_CONNECT_RETRY_DELAY", None)
        else:
            os.environ["DATABASE_CONNECT_RETRY_DELAY"] = original_delay
