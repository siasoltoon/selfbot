import asyncio

import pytest

from selfbot.events import EventEnvelope, EventRouter
from selfbot.errors import ValidationError


@pytest.mark.asyncio
async def test_event_router_dispatches_sync_and_async_handlers():
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

    result = await router.dispatch(event)

    assert result.handled == 2
    assert result.errors == ()
    assert [item[0] for item in seen] == ["sync", "async"]


def test_event_requires_type_and_source():
    with pytest.raises(ValidationError):
        EventEnvelope(event_type="", source="telegram", payload={})

    with pytest.raises(ValidationError):
        EventEnvelope(event_type="x", source="", payload={})
