"""Security monitoring, role checks and emergency lock primitives."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from .errors import AuthorizationError, ValidationError

class Role(StrEnum):
    OWNER="owner"; TRUSTED_USER="trusted_user"; PLUGIN="plugin"

@dataclass(frozen=True, slots=True)
class SecurityEvent:
    kind: str
    actor_id: str | None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict[str, str] = field(default_factory=dict)

class SecurityService:
    def __init__(self, owner_id: str) -> None:
        if not owner_id.strip(): raise ValidationError("owner_id is required")
        self.owner_id=owner_id; self._trusted:set[str]=set(); self._locked=False; self.events:list[SecurityEvent]=[]
    @property
    def emergency_locked(self) -> bool: return self._locked
    def grant_trusted(self, actor_id: str) -> None:
        if not actor_id.strip(): raise ValidationError("actor_id is required")
        self._trusted.add(actor_id)
    def authorize(self, actor_id: str | None, *, owner_only: bool = False) -> None:
        if self._locked and actor_id != self.owner_id: raise AuthorizationError("emergency lock is active")
        if actor_id == self.owner_id: return
        if owner_only or actor_id not in self._trusted: raise AuthorizationError("security permission denied")
    def emergency_lock(self, actor_id: str | None) -> None:
        if actor_id != self.owner_id: raise AuthorizationError("owner permission required")
        self._locked=True; self.events.append(SecurityEvent("emergency_lock", actor_id))
    def unlock(self, actor_id: str | None) -> None:
        if actor_id != self.owner_id: raise AuthorizationError("owner permission required")
        self._locked=False; self.events.append(SecurityEvent("emergency_unlock", actor_id))
