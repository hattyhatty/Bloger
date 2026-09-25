"""build creator intelligence learning loop

Revision ID: 0006_creator_intelligence
Revises: 0005_opportunity_discovery
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0006_creator_intelligence"
down_revision: str | None = "0005_opportunity_discovery"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "creator_learnings",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"),
        sa.Column("creator_profile_id", sa.String(length=128), nullable=False),
        sa.Column("knowledge_entry_id", sa.String(length=128), nullable=True),
        sa.Column("pattern_key", sa.String(length=255), nullable=False),
        sa.Column("learning_statement", sa.Text(), nullable=False),
        sa.Column("learning_type", sa.String(length=64), nullable=False),
        sa.Column("context_key", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("direction", sa.String(length=32), nullable=False, server_default="neutral"),
        sa.Column("supporting_metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("sample_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confidence", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("consistency", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("recency_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("effect_strength", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="proposed"),
        sa.Column("last_validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["creator_profile_id"], ["creator_profiles.id"]),
        sa.ForeignKeyConstraint(["knowledge_entry_id"], ["knowledge_entries.id"]),
        sa.UniqueConstraint("workspace_id", "pattern_key", name="uq_creator_learning_pattern"),
        sa.CheckConstraint("status IN ('proposed', 'active', 'weakened', 'archived')", name="ck_creator_learning_status"),
        sa.CheckConstraint("confidence BETWEEN 0 AND 100", name="ck_creator_learning_confidence"),
        sa.CheckConstraint("consistency BETWEEN 0 AND 100", name="ck_creator_learning_consistency"),
        sa.CheckConstraint("recency_score BETWEEN 0 AND 100", name="ck_creator_learning_recency"),
        sa.CheckConstraint("effect_strength BETWEEN 0 AND 100", name="ck_creator_learning_effect"),
    )
    for column in ("workspace_id", "creator_profile_id", "knowledge_entry_id", "pattern_key", "learning_type", "context_key", "status"):
        op.create_index(f"ix_creator_learnings_{column}", "creator_learnings", [column])

    op.create_table(
        "creator_learning_evidence",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"),
        sa.Column("learning_id", sa.String(length=128), nullable=False),
        sa.Column("content_id", sa.String(length=128), nullable=True),
        sa.Column("opportunity_id", sa.String(length=128), nullable=True),
        sa.Column("publishing_task_id", sa.String(length=128), nullable=True),
        sa.Column("analytics_record_id", sa.String(length=128), nullable=False),
        sa.Column("experience_record_id", sa.String(length=128), nullable=True),
        sa.Column("tracking_snapshot_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("supports", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("outcome_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["learning_id"], ["creator_learnings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["content_id"], ["contents.id"]),
        sa.ForeignKeyConstraint(["opportunity_id"], ["content_opportunities.id"]),
        sa.ForeignKeyConstraint(["publishing_task_id"], ["publishing_tasks.id"]),
        sa.ForeignKeyConstraint(["analytics_record_id"], ["analytics_records.id"]),
        sa.ForeignKeyConstraint(["experience_record_id"], ["experience_records.id"]),
        sa.UniqueConstraint("learning_id", "analytics_record_id", name="uq_learning_analytics_evidence"),
        sa.CheckConstraint("outcome_score BETWEEN -100 AND 100", name="ck_learning_evidence_outcome"),
    )
    for column in ("workspace_id", "learning_id", "content_id", "opportunity_id", "publishing_task_id", "analytics_record_id", "experience_record_id"):
        op.create_index(f"ix_creator_learning_evidence_{column}", "creator_learning_evidence", [column])

    op.create_table(
        "strategy_suggestions",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"),
        sa.Column("creator_profile_id", sa.String(length=128), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("suggestion_type", sa.String(length=64), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("proposed_change", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("rationale", sa.Text(), nullable=False, server_default=""),
        sa.Column("supporting_learning_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["creator_profile_id"], ["creator_profiles.id"]),
        sa.UniqueConstraint("workspace_id", "fingerprint", name="uq_strategy_suggestion_fingerprint"),
        sa.CheckConstraint("status IN ('pending', 'accepted', 'rejected', 'ignored')", name="ck_strategy_suggestion_status"),
    )
    for column in ("workspace_id", "creator_profile_id", "fingerprint", "suggestion_type", "status"):
        op.create_index(f"ix_strategy_suggestions_{column}", "strategy_suggestions", [column])

    op.add_column("content_opportunities", sa.Column("learning_adjustment", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("content_opportunities", sa.Column("learning_explanation", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.add_column("content_opportunities", sa.Column("exploration_bonus", sa.Integer(), nullable=False, server_default="0"))
    op.create_check_constraint("ck_opportunity_learning_adjustment", "content_opportunities", "learning_adjustment BETWEEN -8 AND 8")
    op.create_check_constraint("ck_opportunity_exploration_bonus", "content_opportunities", "exploration_bonus BETWEEN 0 AND 5")

    op.create_table(
        "opportunity_learning_links",
        sa.Column("opportunity_id", sa.String(length=128), nullable=False),
        sa.Column("creator_learning_id", sa.String(length=128), nullable=False),
        sa.ForeignKeyConstraint(["opportunity_id"], ["content_opportunities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["creator_learning_id"], ["creator_learnings.id"]),
        sa.PrimaryKeyConstraint("opportunity_id", "creator_learning_id"),
    )
    op.create_index("ix_opportunity_learning_links_creator_learning_id", "opportunity_learning_links", ["creator_learning_id"])


def downgrade() -> None:
    op.drop_index("ix_opportunity_learning_links_creator_learning_id", table_name="opportunity_learning_links")
    op.drop_table("opportunity_learning_links")
    op.drop_constraint("ck_opportunity_exploration_bonus", "content_opportunities", type_="check")
    op.drop_constraint("ck_opportunity_learning_adjustment", "content_opportunities", type_="check")
    op.drop_column("content_opportunities", "exploration_bonus")
    op.drop_column("content_opportunities", "learning_explanation")
    op.drop_column("content_opportunities", "learning_adjustment")

    for column in reversed(("workspace_id", "creator_profile_id", "fingerprint", "suggestion_type", "status")):
        op.drop_index(f"ix_strategy_suggestions_{column}", table_name="strategy_suggestions")
    op.drop_table("strategy_suggestions")

    for column in reversed(("workspace_id", "learning_id", "content_id", "opportunity_id", "publishing_task_id", "analytics_record_id", "experience_record_id")):
        op.drop_index(f"ix_creator_learning_evidence_{column}", table_name="creator_learning_evidence")
    op.drop_table("creator_learning_evidence")

    for column in reversed(("workspace_id", "creator_profile_id", "knowledge_entry_id", "pattern_key", "learning_type", "context_key", "status")):
        op.drop_index(f"ix_creator_learnings_{column}", table_name="creator_learnings")
    op.drop_table("creator_learnings")
