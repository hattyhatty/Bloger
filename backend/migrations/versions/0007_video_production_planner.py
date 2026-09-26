"""build AI video production planner

Revision ID: 0007_video_planner
Revises: 0006_creator_intelligence
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0007_video_planner"
down_revision: str | None = "0006_creator_intelligence"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "video_production_plans",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"),
        sa.Column("content_id", sa.String(length=128), nullable=False),
        sa.Column("opportunity_id", sa.String(length=128), nullable=True),
        sa.Column("content_revision", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("content_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("video_concept", sa.Text(), nullable=False, server_default=""),
        sa.Column("target_platform", sa.String(length=64), nullable=False, server_default="抖音"),
        sa.Column("target_duration_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("content_format", sa.String(length=128), nullable=False, server_default="口播"),
        sa.Column("visual_style", sa.Text(), nullable=False, server_default=""),
        sa.Column("aspect_ratio", sa.String(length=32), nullable=False, server_default="9:16"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["content_id"], ["contents.id"]),
        sa.ForeignKeyConstraint(["opportunity_id"], ["content_opportunities.id"]),
        sa.UniqueConstraint("workspace_id", "content_id", "content_revision", name="uq_video_plan_content_revision"),
        sa.CheckConstraint("status IN ('draft', 'planned', 'in_production', 'ready_for_review')", name="ck_video_plan_status"),
        sa.CheckConstraint("target_duration_seconds BETWEEN 1 AND 14400", name="ck_video_plan_duration"),
    )
    for column in ("workspace_id", "content_id", "opportunity_id", "content_hash", "target_platform", "status"):
        op.create_index(f"ix_video_production_plans_{column}", "video_production_plans", [column])

    op.create_table(
        "video_scripts",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"),
        sa.Column("plan_id", sa.String(length=128), nullable=False),
        sa.Column("hook", sa.Text(), nullable=False, server_default=""),
        sa.Column("narration_dialogue", sa.Text(), nullable=False, server_default=""),
        sa.Column("main_story_flow", sa.Text(), nullable=False, server_default=""),
        sa.Column("ending_cta", sa.Text(), nullable=False, server_default=""),
        sa.Column("estimated_duration_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("source_context", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["video_production_plans.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("plan_id", name="uq_video_script_plan"),
    )
    op.create_index("ix_video_scripts_workspace_id", "video_scripts", ["workspace_id"])
    op.create_index("ix_video_scripts_plan_id", "video_scripts", ["plan_id"])

    op.create_table(
        "video_storyboards",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"),
        sa.Column("plan_id", sa.String(length=128), nullable=False),
        sa.Column("script_id", sa.String(length=128), nullable=False),
        sa.Column("recurring_character_description", sa.Text(), nullable=False, server_default=""),
        sa.Column("clothing", sa.Text(), nullable=False, server_default=""),
        sa.Column("environment", sa.Text(), nullable=False, server_default=""),
        sa.Column("visual_style", sa.Text(), nullable=False, server_default=""),
        sa.Column("reference_notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["video_production_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["script_id"], ["video_scripts.id"]),
        sa.UniqueConstraint("plan_id", name="uq_video_storyboard_plan"),
    )
    for column in ("workspace_id", "plan_id", "script_id"):
        op.create_index(f"ix_video_storyboards_{column}", "video_storyboards", [column])

    op.create_table(
        "video_shots",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"),
        sa.Column("storyboard_id", sa.String(length=128), nullable=False),
        sa.Column("shot_number", sa.Integer(), nullable=False),
        sa.Column("estimated_duration_seconds", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("scene_description", sa.Text(), nullable=False, server_default=""),
        sa.Column("subject_character", sa.Text(), nullable=False, server_default=""),
        sa.Column("action", sa.Text(), nullable=False, server_default=""),
        sa.Column("environment", sa.Text(), nullable=False, server_default=""),
        sa.Column("camera_framing", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("camera_movement", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("lighting_mood", sa.Text(), nullable=False, server_default=""),
        sa.Column("narration_dialogue", sa.Text(), nullable=False, server_default=""),
        sa.Column("transition", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("generation_notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["storyboard_id"], ["video_storyboards.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("storyboard_id", "shot_number", name="uq_video_shot_number"),
        sa.CheckConstraint("shot_number >= 1", name="ck_video_shot_number"),
        sa.CheckConstraint("estimated_duration_seconds BETWEEN 1 AND 3600", name="ck_video_shot_duration"),
    )
    op.create_index("ix_video_shots_workspace_id", "video_shots", ["workspace_id"])
    op.create_index("ix_video_shots_storyboard_id", "video_shots", ["storyboard_id"])

    op.create_table(
        "video_generation_prompts",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"),
        sa.Column("shot_id", sa.String(length=128), nullable=False),
        sa.Column("prompt_target", sa.String(length=32), nullable=False, server_default="Generic"),
        sa.Column("generic_video_prompt", sa.Text(), nullable=False, server_default=""),
        sa.Column("image_reference_prompt", sa.Text(), nullable=False, server_default=""),
        sa.Column("negative_instructions", sa.Text(), nullable=False, server_default=""),
        sa.Column("continuity_notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("source_shot_hash", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["shot_id"], ["video_shots.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("shot_id", "prompt_target", name="uq_video_prompt_shot_target"),
        sa.CheckConstraint("prompt_target IN ('Generic', 'Seedance', 'Kling', 'Veo', 'Runway')", name="ck_video_prompt_target"),
    )
    for column in ("workspace_id", "shot_id", "prompt_target", "source_shot_hash"):
        op.create_index(f"ix_video_generation_prompts_{column}", "video_generation_prompts", [column])


def downgrade() -> None:
    for column in reversed(("workspace_id", "shot_id", "prompt_target", "source_shot_hash")):
        op.drop_index(f"ix_video_generation_prompts_{column}", table_name="video_generation_prompts")
    op.drop_table("video_generation_prompts")
    op.drop_index("ix_video_shots_storyboard_id", table_name="video_shots")
    op.drop_index("ix_video_shots_workspace_id", table_name="video_shots")
    op.drop_table("video_shots")
    for column in reversed(("workspace_id", "plan_id", "script_id")):
        op.drop_index(f"ix_video_storyboards_{column}", table_name="video_storyboards")
    op.drop_table("video_storyboards")
    op.drop_index("ix_video_scripts_plan_id", table_name="video_scripts")
    op.drop_index("ix_video_scripts_workspace_id", table_name="video_scripts")
    op.drop_table("video_scripts")
    for column in reversed(("workspace_id", "content_id", "opportunity_id", "content_hash", "target_platform", "status")):
        op.drop_index(f"ix_video_production_plans_{column}", table_name="video_production_plans")
    op.drop_table("video_production_plans")
