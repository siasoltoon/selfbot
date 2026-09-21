import asyncio

import pytest

from selfbot.commands import CommandContext, CommandRegistry, CommandSpec
from selfbot.errors import AuthorizationError, ValidationError


class AllowChecker:
    def check(self, actor_id, permission):
        return actor_id == "owner" and permission == "admin"


def test_command_alias_validation_and_execution():
    seen = []

    def handler(context: CommandContext):
        seen.append(context)
        return "ok"

    registry = CommandRegistry(AllowChecker())
    registry.register(
        CommandSpec(
            name="status",
            aliases=("st",),
            permission="admin",
            handler=handler,
        )
    )

    result = asyncio.run(
        registry.execute("st", actor_id="owner", chat_id="chat", arguments={"x": 1})
    )

    assert result == "ok"
    assert seen[0].chat_id == "chat"


def test_permission_is_required_when_declared():
    registry = CommandRegistry(AllowChecker())
    registry.register(
        CommandSpec(name="danger", permission="admin", handler=lambda _: "bad")
    )

    with pytest.raises(AuthorizationError):
        asyncio.run(registry.execute("danger", actor_id="other"))


def test_duplicate_command_is_rejected():
    registry = CommandRegistry()
    spec = CommandSpec(name="ping", handler=lambda _: "pong")
    registry.register(spec)

    with pytest.raises(ValidationError):
        registry.register(spec)
