"""Core command registry with validation and permission boundaries."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from .errors import AuthorizationError, NotFoundError, ValidationError


class PermissionChecker(Protocol):
    def check(self, actor_id: str | None, permission: str) -> bool | Awaitable[bool]:
        """Return whether the actor may perform the named permission."""


ArgumentValidator = Callable[[Mapping[str, Any]], Mapping[str, Any]]
CommandHandler = Callable[["CommandContext"], Any]


@dataclass(frozen=True, slots=True)
class CommandContext:
    actor_id: str | None
    chat_id: str | None
    arguments: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class CommandSpec:
    name: str
    handler: CommandHandler
    aliases: tuple[str, ...] = ()
    permission: str | None = None
    validator: ArgumentValidator | None = None
    description: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("command name must not be empty")
        names = (self.name, *self.aliases)
        if any(not item.strip() for item in names):
            raise ValidationError("command names and aliases must not be empty")


class CommandRegistry:
    """Owns command names, aliases, validation and authorization boundaries."""

    def __init__(self, permission_checker: PermissionChecker | None = None) -> None:
        self._commands: dict[str, CommandSpec] = {}
        self._permission_checker = permission_checker

    def register(self, spec: CommandSpec) -> None:
        for name in (spec.name, *spec.aliases):
            normalized = name.strip().lower()
            if normalized in self._commands:
                raise ValidationError(f"command already registered: {name}")
            self._commands[normalized] = spec

    def unregister(self, name: str) -> bool:
        spec = self._commands.get(name.strip().lower())
        if spec is None:
            return False
        for key, registered in tuple(self._commands.items()):
            if registered is spec:
                del self._commands[key]
        return True

    def resolve(self, name: str) -> CommandSpec:
        spec = self._commands.get(name.strip().lower())
        if spec is None:
            raise NotFoundError(f"command not found: {name}")
        return spec

    def list_commands(self) -> tuple[CommandSpec, ...]:
        unique: dict[str, CommandSpec] = {}
        for spec in self._commands.values():
            unique[spec.name] = spec
        return tuple(unique.values())

    async def execute(
        self,
        name: str,
        *,
        actor_id: str | None = None,
        chat_id: str | None = None,
        arguments: Mapping[str, Any] | None = None,
    ) -> Any:
        spec = self.resolve(name)
        values: Mapping[str, Any] = dict(arguments or {})

        if spec.validator is not None:
            values = spec.validator(values)

        if spec.permission is not None:
            if self._permission_checker is None:
                raise AuthorizationError("command permission checker is not configured")
            allowed = self._permission_checker.check(actor_id, spec.permission)
            if inspect.isawaitable(allowed):
                allowed = await allowed
            if not allowed:
                raise AuthorizationError("command permission denied")

        result = spec.handler(
            CommandContext(
                actor_id=actor_id,
                chat_id=chat_id,
                arguments=values,
            )
        )
        if inspect.isawaitable(result):
            return await result
        return result
