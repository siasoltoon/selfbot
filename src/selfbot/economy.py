"""Internal, provider-independent diamond economy."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable
from sqlalchemy import func, select
from .capabilities import CapabilityService
from .db import Database
from .economy_models import DiamondTransaction, DiamondWallet
from .errors import AuthorizationError, ConflictError, NotFoundError, ValidationError

@dataclass(frozen=True, slots=True)
class EconomyPolicy:
    min_transfer: int = 1
    max_transfer: int = 1_000
    daily_transfer_limit: int = 3_000
    fee_bps: int = 100
    min_fee: int = 1
    max_fee: int = 100
    max_admin_adjustment: int = 100_000

    def __post_init__(self) -> None:
        if self.min_transfer < 1 or self.max_transfer < self.min_transfer:
            raise ValueError("invalid transfer range")
        if self.daily_transfer_limit < self.max_transfer:
            raise ValueError("daily transfer limit must cover max transfer")
        if not 0 <= self.fee_bps <= 10_000:
            raise ValueError("fee_bps must be between 0 and 10000")
        if self.min_fee < 0 or self.max_fee < self.min_fee:
            raise ValueError("invalid fee range")
        if self.max_admin_adjustment < 1:
            raise ValueError("max_admin_adjustment must be positive")

@dataclass(frozen=True, slots=True)
class TransferResult:
    sender_id: str
    recipient_id: str
    amount: int
    fee: int
    sender_balance: int
    recipient_balance: int

@dataclass(frozen=True, slots=True)
class TransactionView:
    id: str
    sender_id: str | None
    recipient_id: str | None
    amount: int
    fee: int
    kind: str
    reason: str | None
    created_at: datetime

class EconomyService:
    """Owns wallet/ledger invariants; Telegram is only an adapter."""

    DOMAIN_CAPABILITY = "panel_diamond_transfer"

    def __init__(
        self,
        database: Database,
        capabilities: CapabilityService,
        *,
        owner_id: str | None = None,
        policy: EconomyPolicy | None = None,
    ) -> None:
        self.database = database
        self.capabilities = capabilities
        self.owner_id = str(owner_id).strip() if owner_id else None
        self.policy = policy or EconomyPolicy()

    @staticmethod
    def _user(user_id: str) -> str:
        value = str(user_id).strip()
        if not value:
            raise ValidationError("user_id is required")
        return value

    def _require_enabled(self, actor_id: str) -> None:
        actor = self._user(actor_id)
        self.capabilities.require(actor, self.DOMAIN_CAPABILITY)

    @staticmethod
    def _fee(amount: int, policy: EconomyPolicy) -> int:
        if policy.fee_bps == 0:
            return 0
        return min(policy.max_fee, max(policy.min_fee, (amount * policy.fee_bps + 9_999) // 10_000))

    def _wallet(self, db, user_id: str, *, lock: bool = False) -> DiamondWallet:
        stmt = select(DiamondWallet).where(DiamondWallet.user_id == user_id)
        if lock:
            stmt = stmt.with_for_update()
        wallet = db.scalar(stmt)
        if wallet is None:
            wallet = DiamondWallet(user_id=user_id, balance=0)
            db.add(wallet)
            db.flush()
            if lock:
                wallet = db.scalar(select(DiamondWallet).where(DiamondWallet.user_id == user_id).with_for_update())
        return wallet

    def balance(self, user_id: str) -> int:
        user = self._user(user_id)
        with self.database.session() as db:
            return int(self._wallet(db, user).balance)

    def ensure_wallet(self, user_id: str) -> int:
        user = self._user(user_id)
        with self.database.session() as db:
            return int(self._wallet(db, user).balance)

    def transfer(self, sender_id: str, recipient_id: str, amount: int) -> TransferResult:
        sender = self._user(sender_id)
        recipient = self._user(recipient_id)
        if sender == recipient:
            raise ValidationError("انتقال الماس به خود مجاز نیست")
        self._require_enabled(self.owner_id or sender)
        if not isinstance(amount, int) or isinstance(amount, bool) or amount < self.policy.min_transfer:
            raise ValidationError(f"حداقل انتقال {self.policy.min_transfer} الماس است")
        if amount > self.policy.max_transfer:
            raise ValidationError(f"حداکثر انتقال {self.policy.max_transfer} الماس است")
        fee = self._fee(amount, self.policy)
        with self.database.session() as db:
            since = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            sent_today = db.scalar(
                select(func.coalesce(func.sum(DiamondTransaction.amount), 0))
                .where(
                    DiamondTransaction.sender_id == sender,
                    DiamondTransaction.kind == "transfer",
                    DiamondTransaction.created_at >= since,
                )
            ) or 0
            if int(sent_today) + amount > self.policy.daily_transfer_limit:
                remaining = max(0, self.policy.daily_transfer_limit - int(sent_today))
                raise ValidationError(f"سقف انتقال روزانه باقی‌مانده {remaining} الماس است")
            sender_wallet = self._wallet(db, sender, lock=True)
            recipient_wallet = self._wallet(db, recipient, lock=True)
            total = amount + fee
            if sender_wallet.balance < total:
                raise ValidationError("موجودی کافی نیست (کارمزد هم از موجودی کسر می‌شود)")
            sender_wallet.balance -= total
            recipient_wallet.balance += amount
            sender_wallet.version += 1
            recipient_wallet.version += 1
            now = datetime.now(timezone.utc)
            sender_wallet.updated_at = now
            recipient_wallet.updated_at = now
            db.add(DiamondTransaction(
                sender_id=sender,
                recipient_id=recipient,
                amount=amount,
                fee=fee,
                kind="transfer",
            ))
            return TransferResult(sender, recipient, amount, fee, sender_wallet.balance, recipient_wallet.balance)

    def adjust(self, actor_id: str, user_id: str, amount: int, *, reason: str | None = None) -> int:
        actor = self._user(actor_id)
        user = self._user(user_id)
        if self.owner_id is None or actor != self.owner_id:
            raise AuthorizationError("admin access denied")
        if not isinstance(amount, int) or isinstance(amount, bool) or amount == 0:
            raise ValidationError("admin adjustment amount must be a non-zero integer")
        if abs(amount) > self.policy.max_admin_adjustment:
            raise ValidationError(f"حداکثر تغییر ادمین {self.policy.max_admin_adjustment} الماس است")
        with self.database.session() as db:
            wallet = self._wallet(db, user, lock=True)
            new_balance = wallet.balance + amount
            if new_balance < 0:
                raise ValidationError("موجودی نمی‌تواند منفی شود")
            wallet.balance = new_balance
            wallet.version += 1
            wallet.updated_at = datetime.now(timezone.utc)
            db.add(DiamondTransaction(
                sender_id=actor if amount < 0 else None,
                recipient_id=user if amount > 0 else None,
                amount=abs(amount),
                fee=0,
                kind="admin_credit" if amount > 0 else "admin_debit",
                reason=(reason or "").strip()[:500] or None,
                actor_id=actor,
            ))
            return int(wallet.balance)

    def history(self, user_id: str, *, limit: int = 20) -> tuple[TransactionView, ...]:
        user = self._user(user_id)
        if not 1 <= limit <= 100:
            raise ValidationError("history limit must be between 1 and 100")
        with self.database.session() as db:
            rows = db.scalars(
                select(DiamondTransaction)
                .where(
                    (DiamondTransaction.sender_id == user) |
                    (DiamondTransaction.recipient_id == user)
                )
                .order_by(DiamondTransaction.created_at.desc())
                .limit(limit)
            ).all()
            return tuple(
                TransactionView(
                    row.id, row.sender_id, row.recipient_id, row.amount, row.fee,
                    row.kind, row.reason, row.created_at,
                ) for row in rows
            )
