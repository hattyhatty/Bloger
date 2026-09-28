"""add shot asset and result tracking

Revision ID: 0008_shot_assets
Revises: 0007_video_planner
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0008_shot_assets"
down_revision: str | None = "0007_video_planner"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "video_reference_assets",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"),
        sa.Column("asset_type", sa.String(length=32), nullable=False, server_default="other"),
        sa.Column("title", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("reference_url", sa.Text(), nullable=False, server_default=""),
        sa.Column("file_reference", sa.Text(), nullable=False, server_default=""),
        sa.Column("note", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.CheckConstraint("asset_type IN ('character', 'clothing', 'environment', 'style', 'other')", name="ck_video_reference_asset_type"),
        sa.CheckConstraint("status IN ('active', 'archived')", name="ck_video_reference_asset_status"),
    )
    for column in ("workspace_id", "asset_type", "status"):
        op.create_index(f"ix_video_reference_assets_{column}", "video_reference_assets", [column])

    op.create_table(
        "video_shot_reference_links",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"),
        sa.Column("shot_id", sa.String(length=128), nullable=False),
        sa.Column("asset_id", sa.String(length=128), nullable=False),
        sa.Column("plan_id", sa.String(length=128), nullable=False),
        sa.Column("plan_content_revision", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["shot_id"], ["video_shots.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["asset_id"], ["video_reference_assets.id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["video_production_plans.id"]),
        sa.UniqueConstraint("shot_id", "asset_id", name="uq_video_shot_reference_link"),
    )
    for column in ("workspace_id", "shot_id", "asset_id", "plan_id"):
        op.create_index(f"ix_video_shot_reference_links_{column}", "video_shot_reference_links", [column])

    op.create_table(
        "video_generation_results",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"),
        sa.Column("plan_id", sa.String(length=128), nullable=False),
        sa.Column("shot_id", sa.String(length=128), nullable=False),
        sa.Column("prompt_id", sa.String(length=128), nullable=False),
        sa.Column("plan_content_revision", sa.Integer(), nullable=False),
        sa.Column("storyboard_revision", sa.Integer(), nullable=False),
        sa.Column("prompt_revision", sa.Integer(), nullable=False),
        sa.Column("shot_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("prompt_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("provider", sa.String(length=64), nullable=False, server_default="External"),
        sa.Column("model", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("result_url", sa.Text(), nullable=False, server_default=""),
        sa.Column("file_reference", sa.Text(), nullable=False, server_default=""),
        sa.Column("note", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="candidate"),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["video_production_plans.id"]),
        sa.ForeignKeyConstraint(["shot_id"], ["video_shots.id"]),
        sa.ForeignKeyConstraint(["prompt_id"], ["video_generation_prompts.id"]),
        sa.CheckConstraint("status IN ('candidate', 'selected', 'rejected', 'archived')", name="ck_video_generation_result_status"),
    )
    for column in ("workspace_id", "plan_id", "shot_id", "prompt_id", "provider", "status"):
        op.create_index(f"ix_video_generation_results_{column}", "video_generation_results", [column])
    op.create_index(
        "uq_video_generation_result_selected_shot",
        "video_generation_results",
        ["shot_id"],
        unique=True,
        postgresql_where=sa.text("status = 'selected'"),
    )


def downgrade() -> None:
    op.drop_index("uq_video_generation_result_selected_shot", table_name="video_generation_results")
    for column in reversed(("workspace_id", "plan_id", "shot_id", "prompt_id", "provider", "status")):
        op.drop_index(f"ix_video_generation_results_{column}", table_name="video_generation_results")
    op.drop_table("video_generation_results")
    for column in reversed(("workspace_id", "shot_id", "asset_id", "plan_id")):
        op.drop_index(f"ix_video_shot_reference_links_{column}", table_name="video_shot_reference_links")
    op.drop_table("video_shot_reference_links")
    for column in reversed(("workspace_id", "asset_type", "status")):
        op.drop_index(f"ix_video_reference_assets_{column}", table_name="video_reference_assets")
    op.drop_table("video_reference_assets")
