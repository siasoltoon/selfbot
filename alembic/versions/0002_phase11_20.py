"""create phase 11-20 domain persistence

Revision ID: 0002_phase11_20
"""
from alembic import op
import sqlalchemy as sa
revision="0002_phase11_20"; down_revision="0001_initial"; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("domain_state",
        sa.Column("id",sa.String(length=36),primary_key=True),
        sa.Column("domain",sa.String(length=80),nullable=False),
        sa.Column("owner_id",sa.String(length=120),nullable=True),
        sa.Column("state",sa.JSON(),nullable=False),
        sa.Column("version",sa.Integer(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_domain_state_domain","domain_state",["domain"])
    op.create_index("ix_domain_state_owner_id","domain_state",["owner_id"])
    op.create_index("ix_domain_state_domain_owner","domain_state",["domain","owner_id"])
    op.create_table("security_audit",
        sa.Column("id",sa.String(length=36),primary_key=True),
        sa.Column("kind",sa.String(length=100),nullable=False),
        sa.Column("actor_id",sa.String(length=120),nullable=True),
        sa.Column("details",sa.JSON(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_security_audit_kind","security_audit",["kind"])
    op.create_index("ix_security_audit_actor_id","security_audit",["actor_id"])
    op.create_index("ix_security_audit_created_at","security_audit",["created_at"])
def downgrade():
    op.drop_table("security_audit")
    op.drop_index("ix_domain_state_domain_owner",table_name="domain_state")
    op.drop_index("ix_domain_state_owner_id",table_name="domain_state")
    op.drop_index("ix_domain_state_domain",table_name="domain_state")
    op.drop_table("domain_state")
