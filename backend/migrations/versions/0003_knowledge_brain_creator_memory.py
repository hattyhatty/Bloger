"""build knowledge brain and creator memory

Revision ID: 0003_knowledge_brain
Revises: 0002_business_workflow
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0003_knowledge_brain"
down_revision: str | None = "0002_business_workflow"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "knowledge_entries",
        sa.Column("knowledge_type", sa.String(length=64), nullable=False, server_default="Source / Research"),
    )
    op.add_column(
        "knowledge_entries",
        sa.Column("source", sa.String(length=255), nullable=False, server_default=""),
    )
    op.add_column(
        "knowledge_entries",
        sa.Column("confidence", sa.Integer(), nullable=False, server_default="70"),
    )
    op.add_column(
        "knowledge_entries",
        sa.Column("status", sa.String(length=64), nullable=False, server_default="ACTIVE"),
    )
    op.create_index("ix_knowledge_entries_knowledge_type", "knowledge_entries", ["knowledge_type"])
    op.create_index("ix_knowledge_entries_source", "knowledge_entries", ["source"])
    op.create_index("ix_knowledge_entries_status", "knowledge_entries", ["status"])
    op.execute("UPDATE knowledge_entries SET source = COALESCE(raw ->> 'source', '') WHERE source = ''")

    op.create_table(
        "creator_profiles",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("account_positioning", sa.Text(), nullable=False, server_default=""),
        sa.Column("target_audience", sa.Text(), nullable=False, server_default=""),
        sa.Column("content_pillars", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("tone_style", sa.Text(), nullable=False, server_default=""),
        sa.Column("preferred_formats", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("topics_to_avoid", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("platform_preferences", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("creator_profiles")
    op.drop_index("ix_knowledge_entries_status", table_name="knowledge_entries")
    op.drop_index("ix_knowledge_entries_source", table_name="knowledge_entries")
    op.drop_index("ix_knowledge_entries_knowledge_type", table_name="knowledge_entries")
    op.drop_column("knowledge_entries", "status")
    op.drop_column("knowledge_entries", "confidence")
    op.drop_column("knowledge_entries", "source")
    op.drop_column("knowledge_entries", "knowledge_type")
