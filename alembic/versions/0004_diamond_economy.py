"""create internal diamond economy

Revision ID: 0004_diamond_economy
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_diamond_economy"
down_revision = "0003_multi_user_telegram"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "diamond_wallets",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=120), nullable=False, unique=True),
        sa.Column("balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("balance >= 0", name="ck_diamond_wallet_balance_nonnegative"),
    )
    op.create_index("ix_diamond_wallets_user_id", "diamond_wallets", ["user_id"], unique=True)
    op.create_table(
        "diamond_transactions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("sender_id", sa.String(length=120), nullable=True),
        sa.Column("recipient_id", sa.String(length=120), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("fee", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("kind", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("actor_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_diamond_transaction_amount_positive"),
        sa.CheckConstraint("fee >= 0", name="ck_diamond_transaction_fee_nonnegative"),
    )
    op.create_index("ix_diamond_transactions_sender_id", "diamond_transactions", ["sender_id"])
    op.create_index("ix_diamond_transactions_recipient_id", "diamond_transactions", ["recipient_id"])
    op.create_index("ix_diamond_transactions_actor_id", "diamond_transactions", ["actor_id"])
    op.create_index("ix_diamond_transactions_kind", "diamond_transactions", ["kind"])
    op.create_index("ix_diamond_transactions_created_at", "diamond_transactions", ["created_at"])
    op.create_index("ix_diamond_transactions_sender_created", "diamond_transactions", ["sender_id", "created_at"])

def downgrade():
    op.drop_index("ix_diamond_transactions_sender_created", table_name="diamond_transactions")
    op.drop_index("ix_diamond_transactions_created_at", table_name="diamond_transactions")
    op.drop_index("ix_diamond_transactions_kind", table_name="diamond_transactions")
    op.drop_index("ix_diamond_transactions_actor_id", table_name="diamond_transactions")
    op.drop_index("ix_diamond_transactions_recipient_id", table_name="diamond_transactions")
    op.drop_index("ix_diamond_transactions_sender_id", table_name="diamond_transactions")
    op.drop_table("diamond_transactions")
    op.drop_index("ix_diamond_wallets_user_id", table_name="diamond_wallets")
    op.drop_table("diamond_wallets")
