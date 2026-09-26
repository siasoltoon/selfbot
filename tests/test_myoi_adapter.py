import asyncio
from types import SimpleNamespace

from selfbot.myoi_adapter import MyoiTelegramAdapter

class FakeButton:
    def __init__(self, text):
        self.text = text
        self.clicked = 0
    async def click(self):
        self.clicked += 1
        return f"clicked:{self.text}"

class FakeClient:
    def __init__(self):
        self.button = FakeButton("🎣 ماهی‌گیری")
        self.sent = []
    async def get_entity(self, username):
        assert username == "MeowieeeQBot"
        return "myoi"
    async def send_message(self, entity, text):
        self.sent.append((entity, text))
        return SimpleNamespace(id=10)
    async def get_messages(self, entity, limit):
        return [SimpleNamespace(id=20, raw_text="منوی میویی", buttons=[[self.button]])]

def test_myoi_adapter_uses_real_bot_username_and_visible_buttons():
    client = FakeClient()
    adapter = MyoiTelegramAdapter(client, bot_username="@MeowieeeQBot")

    async def run():
        await adapter.send_command("/start")
        messages = await adapter.probe()
        result = await adapter.click_button("🎣 ماهی‌گیری")
        return messages, result

    messages, result = asyncio.run(run())
    assert client.sent == [("myoi", "/start")]
    assert messages[0].buttons[0].text == "🎣 ماهی‌گیری"
    assert result == "clicked:🎣 ماهی‌گیری"

def test_myoi_adapter_never_requires_callback_data():
    client = FakeClient()
    adapter = MyoiTelegramAdapter(client)
    message, button = asyncio.run(adapter.find_button("🎣 ماهی‌گیری"))
    assert message.id == 20
    assert button.row == 0
    assert button.column == 0
