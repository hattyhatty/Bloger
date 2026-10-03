"""PostgreSQL durable execution queue.

Revision ID: 0010_durable_queue
Revises: 0009_execution_core
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010_durable_queue"
down_revision = "0009_execution_core"
branch_labels = None
depends_on = None
JSON = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade():
    op.create_table(
        "execution_jobs",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("workspace_id", sa.String(128), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("job_type", sa.String(64), nullable=False),
        sa.Column("subject_type", sa.String(64), nullable=False),
        sa.Column("subject_id", sa.String(128), nullable=False),
        sa.Column("generation_request_id", sa.String(128), sa.ForeignKey("generation_requests.id")),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("payload", JSON, nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("lease_owner", sa.String(128), nullable=False),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True)),
        sa.Column("heartbeat_at", sa.DateTime(timezone=True)),
        sa.Column("last_error", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_execution_job_idempotency_key"),
        sa.CheckConstraint("status IN ('queued','running','succeeded','failed','dead','cancelled')", name="ck_execution_job_status"),
        sa.CheckConstraint("attempt_count >= 0 AND max_attempts > 0", name="ck_execution_job_attempts"),
    )
    op.create_index("ix_execution_jobs_workspace_id", "execution_jobs", ["workspace_id"])
    op.create_index("ix_execution_jobs_job_type", "execution_jobs", ["job_type"])
    op.create_index("ix_execution_jobs_generation_request_id", "execution_jobs", ["generation_request_id"])
    op.create_index("ix_execution_jobs_status", "execution_jobs", ["status"])
    op.create_index("ix_execution_jobs_available_at", "execution_jobs", ["available_at"])
    op.create_index("ix_execution_jobs_lease_expires_at", "execution_jobs", ["lease_expires_at"])
    op.create_index("ix_execution_job_claim", "execution_jobs", ["status", "available_at", "priority"])


def downgrade():
    op.drop_table("execution_jobs")
