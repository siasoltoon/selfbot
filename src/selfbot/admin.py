"""Read-only/controlled administration service primitives for Phase 11."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
from .errors import AuthorizationError, ValidationError

@dataclass(frozen=True, slots=True)
class AdminActor:
    actor_id: str
    role: str = "owner"

@dataclass(frozen=True, slots=True)
class AdminSnapshot:
    bot: dict[str, Any]
    tasks: dict[str, Any]
    workers: dict[str, Any]
    plugins: tuple[dict[str, Any], ...]

class AdminService:
    def __init__(self, owner_id: str, *, metrics: Callable[[], dict[str, Any]] | None = None) -> None:
        if not owner_id.strip(): raise ValidationError("owner_id is required")
        self.owner_id = owner_id
        self.metrics = metrics

    def authorize(self, actor_id: str | None) -> None:
        if actor_id != self.owner_id: raise AuthorizationError("admin access denied")

    def snapshot(self, actor_id: str | None, *, bot: dict[str, Any], tasks: dict[str, Any], workers: dict[str, Any], plugins: tuple[dict[str, Any], ...]) -> AdminSnapshot:
        self.authorize(actor_id)
        data = dict(bot)
        if self.metrics: data["resources"] = dict(self.metrics())
        return AdminSnapshot(data, dict(tasks), dict(workers), tuple(dict(x) for x in plugins))

    def plugin_action(self, actor_id: str | None, action: str, plugin_id: str) -> tuple[str, str]:
        self.authorize(actor_id)
        if action not in {"enable", "disable", "configure"}: raise ValidationError("unsupported plugin action")
        if not plugin_id.strip(): raise ValidationError("plugin_id is required")
        return action, plugin_id
