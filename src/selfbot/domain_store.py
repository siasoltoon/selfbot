"""Small durable JSON domain-state repository."""
from __future__ import annotations
from typing import Any
from sqlalchemy import select
from .db import Database
from .domain_models import DomainState
from .errors import NotFoundError, ValidationError


class DomainStore:
    def __init__(self, database: Database) -> None:
        self.database = database

    def put(self, domain: str, state: dict[str, Any], *, owner_id: str | None = None, record_id: str | None = None) -> str:
        if not domain.strip() or not isinstance(state, dict):
            raise ValidationError("domain and state are required")
        with self.database.session() as s:
            record = s.get(DomainState, record_id) if record_id else None
            if record is None:
                record = DomainState(domain=domain, owner_id=owner_id, state=dict(state))
                s.add(record)
                s.flush()
            else:
                if record.domain != domain or record.owner_id != owner_id:
                    raise ValidationError("domain state ownership mismatch")
                record.state = dict(state)
                record.version += 1
                s.flush()
            return record.id

    def get(self, record_id: str) -> DomainState:
        with self.database.session() as s:
            record = s.get(DomainState, record_id)
            if record is None:
                raise NotFoundError("domain state not found")
            s.expunge(record)
            return record

    def get_by_domain(self, domain: str, owner_id: str | None = None) -> DomainState:
        if not domain.strip():
            raise ValidationError("domain is required")
        with self.database.session() as s:
            record = s.scalar(
                select(DomainState)
                .where(DomainState.domain == domain, DomainState.owner_id == owner_id)
                .order_by(DomainState.updated_at.desc())
                .limit(1)
            )
            if record is None:
                raise NotFoundError("domain state not found")
            s.expunge(record)
            return record
