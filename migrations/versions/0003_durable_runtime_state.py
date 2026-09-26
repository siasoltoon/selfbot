"""Add durable domain, Telegram-session and diamond-economy tables.

Revision ID: 0003_durable_runtime_state
Revises: 0002_tasks
Create Date: 2026-09-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_durable_runtime_state"
down_revision: Union[str, None] = "0002_tasks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "domain_state",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("domain", sa.String(length=80), nullable=False),
        sa.Column("owner_id", sa.String(length=120), nullable=True),
        sa.Column("state", sa.JSON(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_domain_state_domain", "domain_state", ["domain"])
    op.create_index("ix_domain_state_owner_id", "domain_state", ["owner_id"])
    op.create_index("ix_domain_state_domain_owner", "domain_state", ["domain", "owner_id"])

    op.create_table(
        "security_audit",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("kind", sa.String(length=100), nullable=False),
        sa.Column("actor_id", sa.String(length=120), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_security_audit_kind", "security_audit", ["kind"])
    op.create_index("ix_security_audit_actor_id", "security_audit", ["actor_id"])
    op.create_index("ix_security_audit_created_at", "security_audit", ["created_at"])

    op.create_table(
        "telegram_accounts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=120), nullable=False),
        sa.Column("telegram_account_id", sa.String(length=120), nullable=False),
        sa.Column("encrypted_session", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_telegram_accounts_owner_user_id", "telegram_accounts", ["owner_user_id"])
    op.create_index("ix_telegram_accounts_telegram_account_id", "telegram_accounts", ["telegram_account_id"])
    op.create_index("ix_telegram_accounts_status", "telegram_accounts", ["status"])
    op.create_index("ix_telegram_accounts_owner_status", "telegram_accounts", ["owner_user_id", "status"])

    op.create_table(
        "diamond_wallets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=120), nullable=False),
        sa.Column("balance", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("balance >= 0", name="ck_diamond_wallet_balance_nonnegative"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_diamond_wallets_user_id", "diamond_wallets", ["user_id"])

    op.create_table(
        "diamond_transactions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("sender_id", sa.String(length=120), nullable=True),
        sa.Column("recipient_id", sa.String(length=120), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("fee", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("actor_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_diamond_transaction_amount_positive"),
        sa.CheckConstraint("fee >= 0", name="ck_diamond_transaction_fee_nonnegative"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_diamond_transactions_sender_id", "diamond_transactions", ["sender_id"])
    op.create_index("ix_diamond_transactions_recipient_id", "diamond_transactions", ["recipient_id"])
    op.create_index("ix_diamond_transactions_kind", "diamond_transactions", ["kind"])
    op.create_index("ix_diamond_transactions_actor_id", "diamond_transactions", ["actor_id"])
    op.create_index("ix_diamond_transactions_created_at", "diamond_transactions", ["created_at"])
    op.create_index("ix_diamond_transactions_sender_created", "diamond_transactions", ["sender_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_diamond_transactions_sender_created", table_name="diamond_transactions")
    for name in (
        "ix_diamond_transactions_created_at",
        "ix_diamond_transactions_actor_id",
        "ix_diamond_transactions_kind",
        "ix_diamond_transactions_recipient_id",
        "ix_diamond_transactions_sender_id",
    ):
        op.drop_index(name, table_name="diamond_transactions")
    op.drop_table("diamond_transactions")

    op.drop_index("ix_diamond_wallets_user_id", table_name="diamond_wallets")
    op.drop_table("diamond_wallets")

    for name in (
        "ix_telegram_accounts_owner_status",
        "ix_telegram_accounts_status",
        "ix_telegram_accounts_telegram_account_id",
        "ix_telegram_accounts_owner_user_id",
    ):
        op.drop_index(name, table_name="telegram_accounts")
    op.drop_table("telegram_accounts")

    for name in ("ix_security_audit_created_at", "ix_security_audit_actor_id", "ix_security_audit_kind"):
        op.drop_index(name, table_name="security_audit")
    op.drop_table("security_audit")

    for name in ("ix_domain_state_domain_owner", "ix_domain_state_owner_id", "ix_domain_state_domain"):
        op.drop_index(name, table_name="domain_state")
    op.drop_table("domain_state")
