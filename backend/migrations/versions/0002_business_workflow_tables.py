"""create business workflow tables

Revision ID: 0002_business_workflow
Revises: 0001_core_database
Create Date: 2026-08-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_business_workflow"
down_revision = "0001_core_database"
branch_labels = None
depends_on = None


jsonb_default_object = sa.text("'{}'::jsonb")
jsonb_default_array = sa.text("'[]'::jsonb")


def upgrade() -> None:
    op.create_table(
        "platform_versions",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("content_id", sa.String(length=128), sa.ForeignKey("contents.id"), nullable=False),
        sa.Column("platform", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("content_type", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("title", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("hook", sa.Text(), nullable=False, server_default=""),
        sa.Column("body", sa.Text(), nullable=False, server_default=""),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=jsonb_default_array),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="DRAFT"),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=jsonb_default_object),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_platform_versions_content_id", "platform_versions", ["content_id"])
    op.create_index("ix_platform_versions_platform", "platform_versions", ["platform"])
    op.create_index("ix_platform_versions_content_type", "platform_versions", ["content_type"])
    op.create_index("ix_platform_versions_status", "platform_versions", ["status"])

    op.create_table(
        "approval_records",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("content_id", sa.String(length=128), sa.ForeignKey("contents.id"), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="DRAFT"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invalidated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invalidation_reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=jsonb_default_object),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=jsonb_default_object),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_approval_records_content_id", "approval_records", ["content_id"])
    op.create_index("ix_approval_records_status", "approval_records", ["status"])

    op.create_table(
        "publishing_tasks",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("content_id", sa.String(length=128), sa.ForeignKey("contents.id"), nullable=False),
        sa.Column("platform_version_id", sa.String(length=128), sa.ForeignKey("platform_versions.id"), nullable=True),
        sa.Column("platform", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("content_type", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("scheduled_at", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("actual_published_at", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="DRAFT"),
        sa.Column("url", sa.Text(), nullable=False, server_default=""),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=jsonb_default_object),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_publishing_tasks_content_id", "publishing_tasks", ["content_id"])
    op.create_index("ix_publishing_tasks_platform_version_id", "publishing_tasks", ["platform_version_id"])
    op.create_index("ix_publishing_tasks_platform", "publishing_tasks", ["platform"])
    op.create_index("ix_publishing_tasks_content_type", "publishing_tasks", ["content_type"])
    op.create_index("ix_publishing_tasks_scheduled_at", "publishing_tasks", ["scheduled_at"])
    op.create_index("ix_publishing_tasks_status", "publishing_tasks", ["status"])

    op.create_table(
        "analytics_records",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("publishing_task_id", sa.String(length=128), sa.ForeignKey("publishing_tasks.id"), nullable=True),
        sa.Column("content_id", sa.String(length=128), sa.ForeignKey("contents.id"), nullable=True),
        sa.Column("platform", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("content_type", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("stats_date", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("views", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("likes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("comments", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shares", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("saves", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("followers_gained", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tracking_status", sa.String(length=64), nullable=False, server_default="NOT_STARTED"),
        sa.Column("performance_analysis", sa.Text(), nullable=False, server_default=""),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=jsonb_default_object),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_analytics_records_publishing_task_id", "analytics_records", ["publishing_task_id"])
    op.create_index("ix_analytics_records_content_id", "analytics_records", ["content_id"])
    op.create_index("ix_analytics_records_platform", "analytics_records", ["platform"])
    op.create_index("ix_analytics_records_content_type", "analytics_records", ["content_type"])
    op.create_index("ix_analytics_records_tracking_status", "analytics_records", ["tracking_status"])

    op.create_table(
        "tracking_snapshots",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("publishing_task_id", sa.String(length=128), sa.ForeignKey("publishing_tasks.id"), nullable=False),
        sa.Column("analytics_record_id", sa.String(length=128), sa.ForeignKey("analytics_records.id"), nullable=True),
        sa.Column("checkpoint_id", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("label", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("due_at", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="PENDING"),
        sa.Column("stats_date", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=jsonb_default_object),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=jsonb_default_object),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_tracking_snapshots_publishing_task_id", "tracking_snapshots", ["publishing_task_id"])
    op.create_index("ix_tracking_snapshots_analytics_record_id", "tracking_snapshots", ["analytics_record_id"])
    op.create_index("ix_tracking_snapshots_checkpoint_id", "tracking_snapshots", ["checkpoint_id"])
    op.create_index("ix_tracking_snapshots_status", "tracking_snapshots", ["status"])

    op.create_table(
        "experience_records",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("content_id", sa.String(length=128), sa.ForeignKey("contents.id"), nullable=True),
        sa.Column("topic_id", sa.String(length=128), sa.ForeignKey("topics.id"), nullable=True),
        sa.Column("platform_version_id", sa.String(length=128), sa.ForeignKey("platform_versions.id"), nullable=True),
        sa.Column("publishing_task_id", sa.String(length=128), sa.ForeignKey("publishing_tasks.id"), nullable=True),
        sa.Column("analytics_record_id", sa.String(length=128), sa.ForeignKey("analytics_records.id"), nullable=True),
        sa.Column("platform", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("content_type", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("topic_category", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("performance_result", sa.Text(), nullable=False, server_default=""),
        sa.Column("effective_practices", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=jsonb_default_array),
        sa.Column("improvements", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=jsonb_default_array),
        sa.Column("review_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("reviewed_at", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=jsonb_default_object),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_experience_records_content_id", "experience_records", ["content_id"])
    op.create_index("ix_experience_records_topic_id", "experience_records", ["topic_id"])
    op.create_index("ix_experience_records_platform_version_id", "experience_records", ["platform_version_id"])
    op.create_index("ix_experience_records_publishing_task_id", "experience_records", ["publishing_task_id"])
    op.create_index("ix_experience_records_analytics_record_id", "experience_records", ["analytics_record_id"])
    op.create_index("ix_experience_records_platform", "experience_records", ["platform"])
    op.create_index("ix_experience_records_content_type", "experience_records", ["content_type"])
    op.create_index("ix_experience_records_topic_category", "experience_records", ["topic_category"])


def downgrade() -> None:
    op.drop_table("experience_records")
    op.drop_table("tracking_snapshots")
    op.drop_table("analytics_records")
    op.drop_table("publishing_tasks")
    op.drop_table("approval_records")
    op.drop_table("platform_versions")
