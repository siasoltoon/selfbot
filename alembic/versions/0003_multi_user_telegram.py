"""create multi-user Telegram account persistence

Revision ID: 0003_multi_user_telegram
"""
from alembic import op
import sqlalchemy as sa

revision="0003_multi_user_telegram"
down_revision="0002_phase11_20"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table(
        "telegram_accounts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=120), nullable=False),
        sa.Column("telegram_account_id", sa.String(length=120), nullable=False),
        sa.Column("encrypted_session", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_telegram_accounts_owner_user_id","telegram_accounts",["owner_user_id"])
    op.create_index("ix_telegram_accounts_telegram_account_id","telegram_accounts",["telegram_account_id"])
    op.create_index("ix_telegram_accounts_status","telegram_accounts",["status"])
    op.create_index("ix_telegram_accounts_owner_status","telegram_accounts",["owner_user_id","status"])

def downgrade():
    op.drop_index("ix_telegram_accounts_owner_status",table_name="telegram_accounts")
    op.drop_index("ix_telegram_accounts_status",table_name="telegram_accounts")
    op.drop_index("ix_telegram_accounts_telegram_account_id",table_name="telegram_accounts")
    op.drop_index("ix_telegram_accounts_owner_user_id",table_name="telegram_accounts")
    op.drop_table("telegram_accounts")
