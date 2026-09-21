"""Common multi-agent routing abstraction without bypassing core security."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from .errors import AuthorizationError, ValidationError

class Agent(Protocol):
    async def run(self, prompt: str, context: tuple[str, ...] = ()) -> str: ...

@dataclass(frozen=True, slots=True)
class AgentRoute:
    name: str
    permission: str

class AgentRouter:
    def __init__(self) -> None: self._routes: dict[str, tuple[AgentRoute, Agent]] = {}
    def register(self, route: AgentRoute, agent: Agent) -> None:
        if not route.name.strip() or not route.permission.strip(): raise ValidationError("agent route is incomplete")
        if route.name in self._routes: raise ValidationError("agent route already exists")
        self._routes[route.name]=(route,agent)
    async def run(self, name: str, prompt: str, *, allowed_permissions: set[str]) -> str:
        if name not in self._routes: raise ValidationError("agent route not found")
        route,agent=self._routes[name]
        if route.permission not in allowed_permissions: raise AuthorizationError("agent permission denied")
        if not prompt.strip(): raise ValidationError("prompt is empty")
        return await agent.run(prompt)
