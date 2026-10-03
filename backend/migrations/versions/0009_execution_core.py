"""Execution receipts, append-only attempts and version-bound video requests.

Revision ID: 0009_execution_core
Revises: 0008_shot_assets
"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision = "0009_execution_core"
down_revision = "0008_shot_assets"
branch_labels = None
depends_on = None
JSON = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def strings(spec):
    return [sa.Column(name, sa.String(length), nullable=False) for name, length in spec]


def timestamps():
    return [sa.Column(name, sa.DateTime(timezone=True), nullable=False) for name in ("created_at", "updated_at")]


def upgrade():
    op.create_table("external_call_receipts",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("workspace_id", sa.String(128), sa.ForeignKey("workspaces.id"), nullable=False),
        *strings([("service",64),("provider",64),("model",128),("purpose",128),
            ("subject_type",64),("subject_id",128),("logical_key",64),("input_revision",128),
            ("input_hash",64),("prompt_key",128),("prompt_version",64),("prompt_hash",64),
            ("config_hash",64),("status",32),("provider_request_id",255),("currency",16)]),
        *[sa.Column(name, JSON, nullable=False) for name in ("request_summary","response_payload","usage")],
        sa.Column("cost",sa.String(64)),
        sa.Column("received_at",sa.DateTime(timezone=True)),
        sa.Column("completed_at",sa.DateTime(timezone=True)),
        *timestamps(),
        sa.UniqueConstraint("logical_key"),
        sa.CheckConstraint("status IN ('pending','received','completed','failed','unknown')", name="ck_external_receipt_status"))
    op.create_index("ix_external_call_receipts_workspace_id","external_call_receipts",["workspace_id"])
    op.create_table("external_call_attempts",
        sa.Column("id",sa.String(128),primary_key=True),
        sa.Column("receipt_id",sa.String(128),sa.ForeignKey("external_call_receipts.id"),nullable=False),
        sa.Column("attempt_number",sa.Integer(),nullable=False),
        *strings([("status",32),("provider_request_id",255)]),
        sa.Column("started_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("finished_at",sa.DateTime(timezone=True)),
        sa.Column("error",sa.Text(),nullable=False),
        sa.Column("latency_ms",sa.Integer()),
        sa.Column("usage",JSON,nullable=False),
        sa.Column("cost",sa.String(64)),
        sa.UniqueConstraint("receipt_id","attempt_number",name="uq_external_attempt_number"),
        sa.CheckConstraint("status IN ('running','received','completed','failed','unknown')",name="ck_external_attempt_status"))
    op.create_index("ix_external_call_attempts_receipt_id","external_call_attempts",["receipt_id"])
    op.create_index("uq_external_attempt_running","external_call_attempts",["receipt_id"],unique=True,
        postgresql_where=sa.text("status = 'running'"),sqlite_where=sa.text("status = 'running'"))
    op.create_table("generation_requests",
        sa.Column("id",sa.String(128),primary_key=True),
        *[sa.Column(name,sa.String(128),sa.ForeignKey(target),nullable=False) for name,target in (
            ("workspace_id","workspaces.id"),("plan_id","video_production_plans.id"),
            ("shot_id","video_shots.id"),("prompt_id","video_generation_prompts.id"),
            ("receipt_id","external_call_receipts.id"))],
        sa.Column("prompt_revision",sa.Integer(),nullable=False),
        *strings([("provider",64),("model",128),("logical_key",64),("provider_job_id",255),("status",32)]),
        sa.Column("generation_config",JSON,nullable=False),
        sa.Column("input_snapshot",JSON,nullable=False),
        sa.Column("error",sa.Text(),nullable=False),
        *[sa.Column(name,sa.DateTime(timezone=True)) for name in ("queued_at","submitted_at","last_polled_at","completed_at")],
        *timestamps(),sa.UniqueConstraint("logical_key"),sa.UniqueConstraint("receipt_id"),
        sa.CheckConstraint("status IN ('created','queued','submitting','submitted','polling','succeeded','failed','unknown','cancelled')",name="ck_generation_request_status"))
    for name in ("workspace_id","plan_id","shot_id","prompt_id"):
        op.create_index("ix_generation_requests_"+name,"generation_requests",[name])
    op.add_column("video_generation_results",sa.Column("generation_request_id",sa.String(128),nullable=True))
    op.create_foreign_key("fk_video_result_generation_request","video_generation_results","generation_requests",["generation_request_id"],["id"])
    op.create_unique_constraint("uq_video_result_generation_request","video_generation_results",["generation_request_id"])


def downgrade():
    op.drop_constraint("uq_video_result_generation_request","video_generation_results",type_="unique")
    op.drop_constraint("fk_video_result_generation_request","video_generation_results",type_="foreignkey")
    op.drop_column("video_generation_results","generation_request_id")
    op.drop_table("generation_requests")
    op.drop_table("external_call_attempts")
    op.drop_table("external_call_receipts")
