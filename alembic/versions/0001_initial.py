"""initial schema"""
from alembic import op
import sqlalchemy as sa
revision="0001_initial"; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("system_metadata",sa.Column("key",sa.String(100),primary_key=True),sa.Column("value",sa.Text(),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("tasks",sa.Column("id",sa.String(36),primary_key=True),sa.Column("task_type",sa.String(120),nullable=False),sa.Column("owner_id",sa.String(120)),sa.Column("status",sa.String(30),nullable=False),sa.Column("payload",sa.JSON(),nullable=False),sa.Column("result",sa.JSON()),sa.Column("error_code",sa.String(80)),sa.Column("error_message",sa.Text()),sa.Column("attempts",sa.Integer(),nullable=False),sa.Column("max_attempts",sa.Integer(),nullable=False),sa.Column("scheduled_at",sa.DateTime(timezone=True),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
    for n,c in [("ix_tasks_task_type","task_type"),("ix_tasks_owner_id","owner_id"),("ix_tasks_status","status"),("ix_tasks_scheduled_at","scheduled_at")]: op.create_index(n,"tasks",[c])
def downgrade():
    op.drop_table("tasks");op.drop_table("system_metadata")
