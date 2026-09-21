"""Durable domain records for Phase 11-20 state."""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import DateTime, JSON, String, Text, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class DomainState(Base):
    __tablename__="domain_state"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    domain: Mapped[str]=mapped_column(String(80),nullable=False,index=True)
    owner_id: Mapped[str|None]=mapped_column(String(120),nullable=True,index=True)
    state: Mapped[dict]=mapped_column(JSON,nullable=False,default=dict)
    version: Mapped[int]=mapped_column(Integer,nullable=False,default=1)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),nullable=False)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),onupdate=lambda:datetime.now(timezone.utc),nullable=False)
    __table_args__=(Index("ix_domain_state_domain_owner","domain","owner_id"),)

class SecurityAuditRecord(Base):
    __tablename__="security_audit"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    kind: Mapped[str]=mapped_column(String(100),nullable=False,index=True)
    actor_id: Mapped[str|None]=mapped_column(String(120),nullable=True,index=True)
    details: Mapped[dict]=mapped_column(JSON,nullable=False,default=dict)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),nullable=False,index=True)
