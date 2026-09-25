"""build opportunity discovery engine

Revision ID: 0005_opportunity_discovery
Revises: 0004_architecture_hardening
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0005_opportunity_discovery"
down_revision: str | None = "0004_architecture_hardening"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "content_opportunities",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"),
        sa.Column("topic_id", sa.String(length=128), nullable=False),
        sa.Column("creator_profile_id", sa.String(length=128), nullable=False),
        sa.Column("developed_content_id", sa.String(length=128), nullable=True),
        sa.Column("analysis_batch_id", sa.String(length=128), nullable=False),
        sa.Column("angle_key", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("why_it_matters", sa.Text(), nullable=False, server_default=""),
        sa.Column("audience", sa.Text(), nullable=False, server_default=""),
        sa.Column("underlying_need_or_emotion", sa.Text(), nullable=False, server_default=""),
        sa.Column("content_opportunity", sa.Text(), nullable=False),
        sa.Column("recommended_format", sa.String(length=128), nullable=False, server_default=""),
        sa.Column(
            "platform_fit",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("novelty", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("timeliness", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("audience_fit", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("creator_fit", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("human_need_strength", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("platform_fit_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("visual_potential", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("production_difficulty", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overall_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reasoning", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="candidate"),
        sa.Column(
            "raw",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], name="fk_content_opportunities_workspace_id_workspaces"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], name="fk_content_opportunities_topic_id_topics"),
        sa.ForeignKeyConstraint(
            ["creator_profile_id"], ["creator_profiles.id"], name="fk_content_opportunities_creator_profile_id_creator_profiles"
        ),
        sa.ForeignKeyConstraint(
            ["developed_content_id"], ["contents.id"], name="fk_content_opportunities_developed_content_id_contents"
        ),
        sa.CheckConstraint(
            "status IN ('candidate', 'saved', 'rejected', 'developed')",
            name="ck_opportunity_status",
        ),
        sa.CheckConstraint(
            "novelty BETWEEN 0 AND 100 AND timeliness BETWEEN 0 AND 100 "
            "AND audience_fit BETWEEN 0 AND 100 AND creator_fit BETWEEN 0 AND 100 "
            "AND human_need_strength BETWEEN 0 AND 100 AND platform_fit_score BETWEEN 0 AND 100 "
            "AND visual_potential BETWEEN 0 AND 100 AND production_difficulty BETWEEN 0 AND 100 "
            "AND overall_score BETWEEN 0 AND 100",
            name="ck_opportunity_scores",
        ),
        sa.UniqueConstraint(
            "workspace_id", "topic_id", "analysis_batch_id", "angle_key", name="uq_opportunity_batch_angle"
        ),
        sa.UniqueConstraint("developed_content_id", name="uq_opportunity_developed_content"),
    )
    for column in (
        "workspace_id",
        "topic_id",
        "creator_profile_id",
        "developed_content_id",
        "analysis_batch_id",
        "angle_key",
        "overall_score",
        "status",
    ):
        op.create_index(f"ix_content_opportunities_{column}", "content_opportunities", [column])

    op.create_table(
        "opportunity_knowledge_links",
        sa.Column("opportunity_id", sa.String(length=128), nullable=False),
        sa.Column("knowledge_entry_id", sa.String(length=128), nullable=False),
        sa.ForeignKeyConstraint(
            ["opportunity_id"], ["content_opportunities.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["knowledge_entry_id"], ["knowledge_entries.id"]),
        sa.PrimaryKeyConstraint("opportunity_id", "knowledge_entry_id"),
    )
    op.create_index(
        "ix_opportunity_knowledge_links_knowledge_entry_id",
        "opportunity_knowledge_links",
        ["knowledge_entry_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_opportunity_knowledge_links_knowledge_entry_id", table_name="opportunity_knowledge_links")
    op.drop_table("opportunity_knowledge_links")
    for column in reversed((
        "workspace_id",
        "topic_id",
        "creator_profile_id",
        "developed_content_id",
        "analysis_batch_id",
        "angle_key",
        "overall_score",
        "status",
    )):
        op.drop_index(f"ix_content_opportunities_{column}", table_name="content_opportunities")
    op.drop_table("content_opportunities")
