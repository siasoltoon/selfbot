"""Read-only live probe for the real Myoi Telegram bot.

The probe never sends a game command and never clicks a button. It discovers
group chats where the configured Myoi bot has recent messages, then records
visible messages/buttons so workflows can be implemented from observed
Telegram behavior instead of invented APIs.
"""
from __future__ import annotations

import asyncio
import json
import os
from dataclasses import asdict, dataclass
from typing import Any

from selfbot.errors import ConfigurationError
from selfbot.myoi_adapter import MyoiTelegramAdapter


@dataclass(frozen=True, slots=True)
class ProbeGroup:
    chat_id: int
    title: str
    message_count: int
    messages: list[dict[str, Any]]


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigurationError(f"{name} is required")
    return value


def _message_view(message: Any) -> dict[str, Any]:
    buttons = []
    matrix = getattr(message, "buttons", None) or []
    for row_index, row in enumerate(matrix):
        for column_index, button in enumerate(row):
            label = str(getattr(button, "text", "") or "").strip()
            if label:
                buttons.append({"text": label, "row": row_index, "column": column_index})
    text = str(getattr(message, "raw_text", None) or getattr(message, "message", None) or "")
    return {
        "message_id": int(getattr(message, "id", 0) or 0),
        "text": text[:1200],
        "buttons": buttons,
    }


def _build_client(api_id: int, api_hash: str, session: str) -> Any:
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
    except ImportError as exc:
        raise ConfigurationError("Telethon is required for the live Myoi probe") from exc
    return TelegramClient(StringSession(session), api_id, api_hash)


async def probe() -> dict[str, Any]:
    api_id = int(_required("TELEGRAM_API_ID"))
    api_hash = _required("TELEGRAM_API_HASH")
    session = _required("TELEGRAM_SESSION")
    bot_username = os.getenv("MYOI_BOT_USERNAME", "MeowieeeQBot").strip().lstrip("@")
    client = _build_client(api_id, api_hash, session)
    adapter = MyoiTelegramAdapter(client, bot_username=bot_username)

    groups: list[ProbeGroup] = []
    await client.connect()
    try:
        if not await client.is_user_authorized():
            raise ConfigurationError("TELEGRAM_SESSION is not authorized")

        me = await client.get_me()
        bot = await adapter._entity()

        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            is_group = bool(getattr(entity, "megagroup", False) or getattr(entity, "gigagroup", False))
            if not is_group:
                continue

            found = []
            try:
                async for message in client.iter_messages(entity, limit=8, from_user=bot):
                    found.append(message)
            except Exception:
                continue
            if not found:
                continue

            groups.append(
                ProbeGroup(
                    chat_id=int(getattr(entity, "id", 0)),
                    title=str(getattr(entity, "title", "") or dialog.name or "unknown"),
                    message_count=len(found),
                    messages=[_message_view(message) for message in found],
                )
            )

        return {
            "status": "pass",
            "mode": "read_only",
            "account": {
                "id": int(getattr(me, "id", 0)),
                "username": str(getattr(me, "username", "") or ""),
            },
            "myoi_bot": bot_username,
            "groups": [asdict(group) for group in groups],
            "safety": {
                "commands_sent": 0,
                "buttons_clicked": 0,
                "state_changing_actions": 0,
            },
        }
    finally:
        await client.disconnect()


def main() -> None:
    result = asyncio.run(probe())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
