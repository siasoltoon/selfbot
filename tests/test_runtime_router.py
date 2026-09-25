from types import SimpleNamespace

import pytest

from selfbot.events import EventEnvelope, EventRouter
from selfbot.runtime_router import TelegramRuntimeRouter


class FakeTelegram:
    def __init__(self):
        self.events = EventRouter()
        self.sent = []

    async def send_message(self, chat_id, text):
        self.sent.append((chat_id, text))


@pytest.mark.asyncio
async def test_owner_ping_is_routed():
    telegram = FakeTelegram()
    router = TelegramRuntimeRouter(telegram, "42")
    router.start()

    asyncio.run(telegram.events.dispatch(
        EventEnvelope(
            event_type="telegram.new_message",
            source="telegram",
            actor_id="42",
            chat_id="99",
            payload={"text": "/ping"},
        )
    )

    assert telegram.sent == [("99", "pong")]


@pytest.mark.asyncio
async def test_non_owner_command_is_ignored():
    telegram = FakeTelegram()
    router = TelegramRuntimeRouter(telegram, "42")
    router.start()

    asyncio.run(telegram.events.dispatch(
        EventEnvelope(
            event_type="telegram.new_message",
            source="telegram",
            actor_id="7",
            chat_id="99",
            payload={"text": "/ping"},
        )
    )

    assert telegram.sent == []
