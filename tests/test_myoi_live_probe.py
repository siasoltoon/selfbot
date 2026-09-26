from __future__ import annotations

import asyncio
import json

from scripts import myoi_live_probe


class FakeEntity:
    def __init__(self, entity_id: int, title: str, megagroup: bool = True):
        self.id = entity_id
        self.title = title
        self.megagroup = megagroup


class FakeButton:
    def __init__(self, text: str):
        self.text = text


class FakeMessage:
    def __init__(self, message_id: int, text: str, buttons=None):
        self.id = message_id
        self.raw_text = text
        self.buttons = buttons or []


class FakeDialog:
    def __init__(self, entity):
        self.entity = entity
        self.name = entity.title


class FakeClient:
    def __init__(self):
        self.disconnected = False

    async def connect(self):
        pass

    async def disconnect(self):
        self.disconnected = True

    async def is_user_authorized(self):
        return True

    async def get_me(self):
        return FakeEntity(126, "owner")

    async def get_entity(self, username):
        return FakeEntity(999, username, False)

    def iter_dialogs(self):
        async def gen():
            yield FakeDialog(FakeEntity(10, "Myoi Group"))
            yield FakeDialog(FakeEntity(11, "Private", False))
        return gen()

    def iter_messages(self, entity, limit, from_user):
        async def gen():
            yield FakeMessage(55, "سطح ماهی‌گیری: 7", [[FakeButton("ماهی‌گیری"), FakeButton("پیشی")]])
        return gen()


def test_message_view_is_read_only_metadata():
    message = FakeMessage(1, "سلام", [[FakeButton("پیشی")]])
    view = myoi_live_probe._message_view(message)
    assert view["buttons"][0]["text"] == "پیشی"
    assert view["text"] == "سلام"


def test_probe_does_not_send_or_click(monkeypatch):
    fake = FakeClient()

    class FakeTelegramClient:
        def __new__(cls, *args, **kwargs):
            return fake

    monkeypatch.setitem(__import__("sys").modules, "telethon", type("Telethon", (), {"TelegramClient": FakeTelegramClient, "sessions": type("S", (), {"StringSession": object})})())
    monkeypatch.setattr(myoi_live_probe, "MyoiTelegramAdapter", lambda client, bot_username: type("A", (), {"_entity": lambda self: asyncio.sleep(0, result=FakeEntity(999, bot_username))})())

    result = asyncio.run(_run_probe())
    assert result["safety"]["commands_sent"] == 0
    assert result["safety"]["buttons_clicked"] == 0
    assert result["groups"][0]["title"] == "Myoi Group"


async def _run_probe():
    return await myoi_live_probe.probe()
