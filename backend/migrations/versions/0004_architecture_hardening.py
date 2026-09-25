"""audit and harden core architecture

Revision ID: 0004_architecture_hardening
Revises: 0003_knowledge_brain
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0004_architecture_hardening"
down_revision: str | None = "0003_knowledge_brain"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


OWNED_TABLES = (
    "topics",
    "contents",
    "knowledge_entries",
    "creator_profiles",
    "platform_versions",
    "approval_records",
    "publishing_tasks",
    "analytics_records",
    "tracking_snapshots",
    "experience_records",
)


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, server_default="Default Workspace"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.execute("INSERT INTO workspaces (id, name) VALUES ('default', 'Default Workspace')")

    for table_name in OWNED_TABLES:
        op.add_column(table_name, sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"))
        op.create_index(f"ix_{table_name}_workspace_id", table_name, ["workspace_id"])
        op.create_foreign_key(
            f"fk_{table_name}_workspace_id_workspaces",
            table_name,
            "workspaces",
            ["workspace_id"],
            ["id"],
        )

    op.add_column("activity_logs", sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="default"))
    op.create_index("ix_activity_logs_workspace_id", "activity_logs", ["workspace_id"])
    op.create_unique_constraint("uq_creator_profiles_workspace", "creator_profiles", ["workspace_id"])

    op.add_column("contents", sa.Column("revision", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("contents", sa.Column("content_hash", sa.String(length=64), nullable=False, server_default=""))
    op.create_index("ix_contents_content_hash", "contents", ["content_hash"])
    op.execute(
        "UPDATE contents SET content_hash = md5(concat_ws('|', title, platform, content_type, source_url, raw::text)) "
        "WHERE content_hash = ''"
    )

    op.add_column("platform_versions", sa.Column("revision", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("platform_versions", sa.Column("content_hash", sa.String(length=64), nullable=False, server_default=""))
    op.add_column("platform_versions", sa.Column("is_immutable", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.create_index("ix_platform_versions_content_hash", "platform_versions", ["content_hash"])
    op.execute(
        """
        WITH ranked AS (
          SELECT id, row_number() OVER (
            PARTITION BY content_id, platform, content_type ORDER BY created_at, id
          ) AS next_revision
          FROM platform_versions
        )
        UPDATE platform_versions AS pv
        SET revision = ranked.next_revision,
            content_hash = md5(concat_ws('|', pv.title, pv.hook, pv.body, pv.tags::text, pv.platform, pv.content_type))
        FROM ranked
        WHERE pv.id = ranked.id
        """
    )
    op.execute(
        """
        UPDATE platform_versions AS pv
        SET is_immutable = true
        WHERE EXISTS (SELECT 1 FROM publishing_tasks pt WHERE pt.platform_version_id = pv.id)
           OR lower(pv.status) IN ('approved', 'ready_to_publish', 'published')
        """
    )
    op.create_unique_constraint(
        "uq_platform_version_revision",
        "platform_versions",
        ["content_id", "platform", "content_type", "revision"],
    )

    op.add_column("approval_records", sa.Column("platform_version_id", sa.String(length=128), nullable=True))
    op.add_column("approval_records", sa.Column("platform_version_revision", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("approval_records", sa.Column("snapshot_hash", sa.String(length=64), nullable=False, server_default=""))
    op.create_index("ix_approval_records_platform_version_id", "approval_records", ["platform_version_id"])
    op.create_index("ix_approval_records_snapshot_hash", "approval_records", ["snapshot_hash"])
    op.create_foreign_key(
        "fk_approval_records_platform_version_id_platform_versions",
        "approval_records",
        "platform_versions",
        ["platform_version_id"],
        ["id"],
    )
    op.execute(
        """
        UPDATE approval_records AS ar
        SET platform_version_id = (
              SELECT pv.id FROM platform_versions pv
              WHERE pv.content_id = ar.content_id
              ORDER BY pv.is_immutable DESC, pv.updated_at DESC, pv.id LIMIT 1
            ),
            platform_version_revision = COALESCE((
              SELECT pv.revision FROM platform_versions pv
              WHERE pv.content_id = ar.content_id
              ORDER BY pv.is_immutable DESC, pv.updated_at DESC, pv.id LIMIT 1
            ), 0),
            snapshot_hash = md5(ar.snapshot::text)
        """
    )

    op.add_column("publishing_tasks", sa.Column("approval_record_id", sa.String(length=128), nullable=True))
    op.add_column("publishing_tasks", sa.Column("content_revision", sa.Integer(), nullable=False, server_default="1"))
    op.add_column(
        "publishing_tasks",
        sa.Column("version_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("ix_publishing_tasks_approval_record_id", "publishing_tasks", ["approval_record_id"])
    op.create_foreign_key(
        "fk_publishing_tasks_approval_record_id_approval_records",
        "publishing_tasks",
        "approval_records",
        ["approval_record_id"],
        ["id"],
    )
    op.execute(
        """
        UPDATE publishing_tasks AS pt
        SET content_revision = c.revision,
            version_snapshot = jsonb_build_object(
              'platformVersionId', pv.id,
              'revision', pv.revision,
              'contentHash', pv.content_hash,
              'title', pv.title,
              'hook', pv.hook,
              'body', pv.body,
              'tags', pv.tags,
              'platform', pv.platform,
              'contentType', pv.content_type
            )
        FROM contents c, platform_versions pv
        WHERE pt.content_id = c.id AND pt.platform_version_id = pv.id
        """
    )
    op.execute(
        """
        UPDATE publishing_tasks AS pt
        SET approval_record_id = (
          SELECT ar.id
          FROM approval_records ar
          WHERE ar.content_id = pt.content_id
            AND (ar.platform_version_id = pt.platform_version_id OR ar.platform_version_id IS NULL)
            AND lower(replace(ar.status, ' ', '_')) IN ('approved', 'ready_to_publish')
          ORDER BY ar.approved_at DESC NULLS LAST, ar.updated_at DESC
          LIMIT 1
        )
        """
    )
    op.create_unique_constraint(
        "uq_publishing_version_schedule",
        "publishing_tasks",
        ["workspace_id", "content_id", "platform_version_id", "scheduled_at"],
    )

    op.create_unique_constraint("uq_analytics_publishing_task", "analytics_records", ["publishing_task_id"])

    op.add_column("tracking_snapshots", sa.Column("sequence", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("tracking_snapshots", sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    op.create_index("ix_tracking_snapshots_recorded_at", "tracking_snapshots", ["recorded_at"])
    op.execute(
        """
        WITH ranked AS (
          SELECT id, row_number() OVER (
            PARTITION BY publishing_task_id, checkpoint_id ORDER BY created_at, id
          ) AS next_sequence
          FROM tracking_snapshots
        )
        UPDATE tracking_snapshots AS ts
        SET sequence = ranked.next_sequence, recorded_at = ts.updated_at
        FROM ranked
        WHERE ts.id = ranked.id
        """
    )
    op.create_unique_constraint(
        "uq_tracking_checkpoint_sequence",
        "tracking_snapshots",
        ["publishing_task_id", "checkpoint_id", "sequence"],
    )

    op.create_unique_constraint("uq_experience_publishing_task", "experience_records", ["publishing_task_id"])


def downgrade() -> None:
    op.drop_constraint("uq_experience_publishing_task", "experience_records", type_="unique")

    op.drop_constraint("uq_tracking_checkpoint_sequence", "tracking_snapshots", type_="unique")
    op.drop_index("ix_tracking_snapshots_recorded_at", table_name="tracking_snapshots")
    op.drop_column("tracking_snapshots", "recorded_at")
    op.drop_column("tracking_snapshots", "sequence")

    op.drop_constraint("uq_analytics_publishing_task", "analytics_records", type_="unique")

    op.drop_constraint("uq_publishing_version_schedule", "publishing_tasks", type_="unique")
    op.drop_constraint("fk_publishing_tasks_approval_record_id_approval_records", "publishing_tasks", type_="foreignkey")
    op.drop_index("ix_publishing_tasks_approval_record_id", table_name="publishing_tasks")
    op.drop_column("publishing_tasks", "version_snapshot")
    op.drop_column("publishing_tasks", "content_revision")
    op.drop_column("publishing_tasks", "approval_record_id")

    op.drop_constraint("fk_approval_records_platform_version_id_platform_versions", "approval_records", type_="foreignkey")
    op.drop_index("ix_approval_records_snapshot_hash", table_name="approval_records")
    op.drop_index("ix_approval_records_platform_version_id", table_name="approval_records")
    op.drop_column("approval_records", "snapshot_hash")
    op.drop_column("approval_records", "platform_version_revision")
    op.drop_column("approval_records", "platform_version_id")

    op.drop_constraint("uq_platform_version_revision", "platform_versions", type_="unique")
    op.drop_index("ix_platform_versions_content_hash", table_name="platform_versions")
    op.drop_column("platform_versions", "is_immutable")
    op.drop_column("platform_versions", "content_hash")
    op.drop_column("platform_versions", "revision")

    op.drop_index("ix_contents_content_hash", table_name="contents")
    op.drop_column("contents", "content_hash")
    op.drop_column("contents", "revision")

    op.drop_constraint("uq_creator_profiles_workspace", "creator_profiles", type_="unique")
    op.drop_index("ix_activity_logs_workspace_id", table_name="activity_logs")
    op.drop_column("activity_logs", "workspace_id")

    for table_name in reversed(OWNED_TABLES):
        op.drop_constraint(f"fk_{table_name}_workspace_id_workspaces", table_name, type_="foreignkey")
        op.drop_index(f"ix_{table_name}_workspace_id", table_name=table_name)
        op.drop_column(table_name, "workspace_id")

    op.drop_table("workspaces")
