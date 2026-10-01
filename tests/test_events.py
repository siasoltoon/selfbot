import asyncio

import pytest

from selfbot.events import EventEnvelope, EventRouter
from selfbot.errors import ValidationError


def test_event_router_dispatches_sync_and_async_handlers():
    router = EventRouter()
    seen = []

    def sync_handler(event):
        seen.append(("sync", event.event_id))

    async def async_handler(event):
        await asyncio.sleep(0)
        seen.append(("async", event.event_id))

    router.subscribe("message.created", sync_handler)
    router.subscribe("message.created", async_handler)

    event = EventEnvelope(
        event_type="message.created",
        source="telegram",
        payload={"text": "hello"},
    )

    result = asyncio.run(router.dispatch(event))

    assert result.handled == 2
    assert result.errors == ()
    assert [item[0] for item in seen] == ["sync", "async"]


def test_event_requires_type_and_source():
    with pytest.raises(ValidationError):
        EventEnvelope(event_type="", source="telegram", payload={})

    with pytest.raises(ValidationError):
        EventEnvelope(event_type="x", source="", payload={})


def test_event_router_logs_handler_failure(caplog):
    router = EventRouter()

    async def broken(_event):
        raise RuntimeError("database link dropped")

    router.subscribe("telegram.new_message", broken)
    event = EventEnvelope(
        event_type="telegram.new_message",
        source="telegram.account.123",
        actor_id="42",
        chat_id="99",
        payload={"text": "/status"},
    )

    caplog.set_level("ERROR", logger="selfbot.events")
    result = asyncio.run(router.dispatch(event))

    assert result.handled == 0
    assert len(result.errors) == 1
    records = [r for r in caplog.records if r.message == "event handler failed"]
    assert len(records) == 1
    assert records[0].context["event_id"] == event.event_id
    assert records[0].context["correlation_id"] == event.correlation_id
    assert records[0].context["exception_type"] == "RuntimeError"
