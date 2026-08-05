"""create core database tables

Revision ID: 0001_core_database
Revises:
Create Date: 2026-08-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_core_database"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "topics",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("source", sa.String(length=64), nullable=False, server_default="mock"),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("url", sa.Text(), nullable=False, server_default=""),
        sa.Column("author", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("category", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="DISCOVERED"),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_topics_source", "topics", ["source"])
    op.create_index("ix_topics_title", "topics", ["title"])
    op.create_index("ix_topics_category", "topics", ["category"])
    op.create_index("ix_topics_status", "topics", ["status"])

    op.create_table(
        "contents",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("topic_id", sa.String(length=128), sa.ForeignKey("topics.id"), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="DRAFT"),
        sa.Column("platform", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("content_type", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("source_url", sa.Text(), nullable=False, server_default=""),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_contents_topic_id", "contents", ["topic_id"])
    op.create_index("ix_contents_title", "contents", ["title"])
    op.create_index("ix_contents_status", "contents", ["status"])
    op.create_index("ix_contents_platform", "contents", ["platform"])
    op.create_index("ix_contents_content_type", "contents", ["content_type"])

    op.create_table(
        "knowledge_entries",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("topic_id", sa.String(length=128), sa.ForeignKey("topics.id"), nullable=True),
        sa.Column("content_id", sa.String(length=128), sa.ForeignKey("contents.id"), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("body", sa.Text(), nullable=False, server_default=""),
        sa.Column("source_url", sa.Text(), nullable=False, server_default=""),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_knowledge_entries_topic_id", "knowledge_entries", ["topic_id"])
    op.create_index("ix_knowledge_entries_content_id", "knowledge_entries", ["content_id"])
    op.create_index("ix_knowledge_entries_title", "knowledge_entries", ["title"])

    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=128), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_activity_logs_action", "activity_logs", ["action"])
    op.create_index("ix_activity_logs_entity_type", "activity_logs", ["entity_type"])
    op.create_index("ix_activity_logs_entity_id", "activity_logs", ["entity_id"])
    op.create_index("ix_activity_logs_created_at", "activity_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("activity_logs")
    op.drop_table("knowledge_entries")
    op.drop_table("contents")
    op.drop_table("topics")
