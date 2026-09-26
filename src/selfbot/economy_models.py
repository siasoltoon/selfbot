"""Persistent internal diamond economy models."""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class DiamondWallet(Base):
    __tablename__ = "diamond_wallets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    __table_args__ = (CheckConstraint("balance >= 0", name="ck_diamond_wallet_balance_nonnegative"),)

class DiamondTransaction(Base):
    __tablename__ = "diamond_transactions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    sender_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    recipient_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    fee: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    kind: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    actor_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_diamond_transaction_amount_positive"),
        CheckConstraint("fee >= 0", name="ck_diamond_transaction_fee_nonnegative"),
        Index("ix_diamond_transactions_sender_created", "sender_id", "created_at"),
    )
