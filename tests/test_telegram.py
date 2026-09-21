import asyncio
from dataclasses import replace

import pytest

from selfbot.errors import ConfigurationError
from selfbot.telegram import TelegramAdapter


class FakeClient:
    def __init__(self):
        self.started = False
        self.stopped = False
        self.handlers = []
        self.sent = []

    async def start(self):
        self.started = True

    async def stop(self):
        self.stopped = True

    async def send_message(self, chat_id, text):
        self.sent.append((chat_id, text))
        return {"ok": True}

    def add_event_handler(self, handler):
        self.handlers.append(handler)


def test_telegram_adapter_rejects_missing_credentials(test_settings):
    adapter = TelegramAdapter(test_settings, events=None)
    with pytest.raises(ConfigurationError):
        asyncio.run(adapter.start())


def test_telegram_adapter_lifecycle_and_send(test_settings):
    settings = replace(
        test_settings,
        telegram_api_id="12345",
        telegram_api_hash="hash",
        telegram_session="test-session",
    )
    client = FakeClient()
    adapter = TelegramAdapter(settings, events=__import__("selfbot.events", fromlist=["EventRouter"]).EventRouter(), client_factory=lambda _: client)

    asyncio.run(adapter.start())
    assert adapter.started is True
    assert client.started is True
    assert len(client.handlers) == 1

    result = asyncio.run(adapter.send_message("1", "hello"))
    assert result == {"ok": True}

    asyncio.run(adapter.stop())
    asyncio.run(adapter.stop())
    assert adapter.started is False
    assert client.stopped is True
