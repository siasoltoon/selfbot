import asyncio

from selfbot.events import EventEnvelope, EventRouter
from selfbot.runtime_router import TelegramRuntimeRouter


class FakeTelegram:
    def __init__(self):
        self.events = EventRouter()
        self.sent = []

    async def send_message(self, chat_id, text, *, account_id=None):
        self.sent.append((chat_id, text, account_id))


def test_owner_ping_is_routed():
    telegram = FakeTelegram()
    router = TelegramRuntimeRouter(telegram, "42")
    router.start()

    asyncio.run(
        telegram.events.dispatch(
            EventEnvelope(
                event_type="telegram.new_message",
                source="telegram",
                actor_id="42",
                chat_id="99",
                payload={"text": "/ping"},
            )
        )
    )

    assert telegram.sent == [("99", "pong", None)]


def test_non_owner_command_is_ignored():
    telegram = FakeTelegram()
    router = TelegramRuntimeRouter(telegram, "42")
    router.start()

    asyncio.run(
        telegram.events.dispatch(
            EventEnvelope(
                event_type="telegram.new_message",
                source="telegram",
                actor_id="7",
                chat_id="99",
                payload={"text": "/ping"},
            )
        )
    )

    assert telegram.sent == []


def test_linked_account_ping_is_routed_to_its_account():
    telegram = FakeTelegram()
    router = TelegramRuntimeRouter(telegram, None, allow_linked_accounts=True)
    router.start()

    asyncio.run(
        telegram.events.dispatch(
            EventEnvelope(
                event_type="telegram.new_message",
                source="telegram.account.123",
                actor_id="42",
                chat_id="99",
                payload={"text": "/ping", "telegram_account_id": "123"},
            )
        )
    )

    assert telegram.sent == [("99", "pong", "123")]
