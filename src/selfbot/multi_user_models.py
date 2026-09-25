"""Persistent records for multi-user Telegram selfbot accounts."""
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class TelegramAccount(Base):
    __tablename__ = "telegram_accounts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_user_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    telegram_account_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    encrypted_session: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="connected", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    __table_args__ = (Index("ix_telegram_accounts_owner_status", "owner_user_id", "status"),)
