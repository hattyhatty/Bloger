"""Durable generated asset storage.

Revision ID: 0011_generated_assets
Revises: 0010_durable_queue
"""
from alembic import op
import sqlalchemy as sa


revision = "0011_generated_assets"
down_revision = "0010_durable_queue"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "generated_assets",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("workspace_id", sa.String(128), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("generation_result_id", sa.String(128), sa.ForeignKey("video_generation_results.id"), nullable=False),
        sa.Column("source_provider", sa.String(64), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("storage_provider", sa.String(64), nullable=False),
        sa.Column("storage_key", sa.String(255), nullable=False),
        sa.Column("durable_url", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.String(128), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=False),
        sa.Column("stored_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("generation_result_id", name="uq_generated_asset_result"),
        sa.UniqueConstraint("storage_provider", "storage_key", name="uq_generated_asset_storage_key"),
        sa.CheckConstraint("status IN ('pending','stored','failed','archived')", name="ck_generated_asset_status"),
        sa.CheckConstraint("file_size >= 0", name="ck_generated_asset_file_size"),
    )
    op.create_index("ix_generated_assets_workspace_id", "generated_assets", ["workspace_id"])
    op.create_index("ix_generated_assets_generation_result_id", "generated_assets", ["generation_result_id"])
    op.create_index("ix_generated_assets_status", "generated_assets", ["status"])


def downgrade():
    op.drop_table("generated_assets")
