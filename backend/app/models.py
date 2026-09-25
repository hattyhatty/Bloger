from datetime import datetime, timezone

from sqlalchemy import Boolean, JSON, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

JsonType = JSON().with_variant(JSONB, "postgresql")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class Workspace(Base, TimestampMixin):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(128), primary_key=True, default="default")
    name: Mapped[str] = mapped_column(String(255), default="Default Workspace")


class Topic(Base, TimestampMixin):
    __tablename__ = "topics"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    source: Mapped[str] = mapped_column(String(64), index=True, default="mock")
    title: Mapped[str] = mapped_column(String(512), index=True)
    url: Mapped[str] = mapped_column(Text, default="")
    author: Mapped[str] = mapped_column(String(255), default="")
    category: Mapped[str] = mapped_column(String(128), index=True, default="")
    status: Mapped[str] = mapped_column(String(64), index=True, default="DISCOVERED")
    score: Mapped[int] = mapped_column(Integer, default=0)
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    contents: Mapped[list["Content"]] = relationship(back_populates="topic")
    knowledge_entries: Mapped[list["KnowledgeEntry"]] = relationship(back_populates="topic")


class Content(Base, TimestampMixin):
    __tablename__ = "contents"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    topic_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("topics.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(512), index=True)
    status: Mapped[str] = mapped_column(String(64), index=True, default="DRAFT")
    platform: Mapped[str] = mapped_column(String(64), index=True, default="")
    content_type: Mapped[str] = mapped_column(String(64), index=True, default="")
    source_url: Mapped[str] = mapped_column(Text, default="")
    revision: Mapped[int] = mapped_column(Integer, default=1)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, default="")
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    topic: Mapped[Topic | None] = relationship(back_populates="contents")
    knowledge_entries: Mapped[list["KnowledgeEntry"]] = relationship(back_populates="content")
    platform_versions: Mapped[list["PlatformVersion"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    approval_records: Mapped[list["ApprovalRecord"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    publishing_tasks: Mapped[list["PublishingTask"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    analytics_records: Mapped[list["AnalyticsRecord"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    experience_records: Mapped[list["ExperienceRecord"]] = relationship(back_populates="content")


class KnowledgeEntry(Base, TimestampMixin):
    __tablename__ = "knowledge_entries"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    topic_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("topics.id"), nullable=True, index=True)
    content_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("contents.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(512), index=True)
    body: Mapped[str] = mapped_column(Text, default="")
    knowledge_type: Mapped[str] = mapped_column(String(64), index=True, default="Source / Research")
    source: Mapped[str] = mapped_column(String(255), index=True, default="")
    source_url: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[list] = mapped_column(JsonType, default=list)
    confidence: Mapped[int] = mapped_column(Integer, default=70)
    status: Mapped[str] = mapped_column(String(64), index=True, default="ACTIVE")
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    topic: Mapped[Topic | None] = relationship(back_populates="knowledge_entries")
    content: Mapped[Content | None] = relationship(back_populates="knowledge_entries")


class CreatorProfile(Base, TimestampMixin):
    __tablename__ = "creator_profiles"
    __table_args__ = (UniqueConstraint("workspace_id", name="uq_creator_profiles_workspace"),)

    id: Mapped[str] = mapped_column(String(128), primary_key=True, default="default")
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    account_positioning: Mapped[str] = mapped_column(Text, default="")
    target_audience: Mapped[str] = mapped_column(Text, default="")
    content_pillars: Mapped[list] = mapped_column(JsonType, default=list)
    tone_style: Mapped[str] = mapped_column(Text, default="")
    preferred_formats: Mapped[list] = mapped_column(JsonType, default=list)
    topics_to_avoid: Mapped[list] = mapped_column(JsonType, default=list)
    platform_preferences: Mapped[list] = mapped_column(JsonType, default=list)
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)


class PlatformVersion(Base, TimestampMixin):
    __tablename__ = "platform_versions"
    __table_args__ = (
        UniqueConstraint("content_id", "platform", "content_type", "revision", name="uq_platform_version_revision"),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    content_id: Mapped[str] = mapped_column(String(128), ForeignKey("contents.id"), index=True)
    platform: Mapped[str] = mapped_column(String(64), index=True, default="")
    content_type: Mapped[str] = mapped_column(String(64), index=True, default="")
    title: Mapped[str] = mapped_column(String(512), default="")
    hook: Mapped[str] = mapped_column(Text, default="")
    body: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[list] = mapped_column(JsonType, default=list)
    status: Mapped[str] = mapped_column(String(64), index=True, default="DRAFT")
    revision: Mapped[int] = mapped_column(Integer, default=1)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, default="")
    is_immutable: Mapped[bool] = mapped_column(Boolean, default=False)
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    content: Mapped[Content] = relationship(back_populates="platform_versions")
    publishing_tasks: Mapped[list["PublishingTask"]] = relationship(back_populates="platform_version")
    experience_records: Mapped[list["ExperienceRecord"]] = relationship(back_populates="platform_version")


class ApprovalRecord(Base, TimestampMixin):
    __tablename__ = "approval_records"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    content_id: Mapped[str] = mapped_column(String(128), ForeignKey("contents.id"), index=True)
    platform_version_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("platform_versions.id"), nullable=True, index=True)
    platform_version_revision: Mapped[int] = mapped_column(Integer, default=0)
    snapshot_hash: Mapped[str] = mapped_column(String(64), index=True, default="")
    status: Mapped[str] = mapped_column(String(64), index=True, default="DRAFT")
    notes: Mapped[str] = mapped_column(Text, default="")
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    invalidation_reason: Mapped[str] = mapped_column(Text, default="")
    snapshot: Mapped[dict] = mapped_column(JsonType, default=dict)
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    content: Mapped[Content] = relationship(back_populates="approval_records")


class PublishingTask(Base, TimestampMixin):
    __tablename__ = "publishing_tasks"
    __table_args__ = (
        UniqueConstraint("workspace_id", "content_id", "platform_version_id", "scheduled_at", name="uq_publishing_version_schedule"),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    content_id: Mapped[str] = mapped_column(String(128), ForeignKey("contents.id"), index=True)
    platform_version_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("platform_versions.id"), nullable=True, index=True)
    approval_record_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("approval_records.id"), nullable=True, index=True)
    content_revision: Mapped[int] = mapped_column(Integer, default=1)
    version_snapshot: Mapped[dict] = mapped_column(JsonType, default=dict)
    platform: Mapped[str] = mapped_column(String(64), index=True, default="")
    content_type: Mapped[str] = mapped_column(String(64), index=True, default="")
    scheduled_at: Mapped[str] = mapped_column(String(64), index=True, default="")
    actual_published_at: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(64), index=True, default="DRAFT")
    url: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    content: Mapped[Content] = relationship(back_populates="publishing_tasks")
    platform_version: Mapped[PlatformVersion | None] = relationship(back_populates="publishing_tasks")
    analytics_records: Mapped[list["AnalyticsRecord"]] = relationship(back_populates="publishing_task", cascade="all, delete-orphan")
    tracking_snapshots: Mapped[list["TrackingSnapshot"]] = relationship(back_populates="publishing_task", cascade="all, delete-orphan")
    experience_records: Mapped[list["ExperienceRecord"]] = relationship(back_populates="publishing_task")


class AnalyticsRecord(Base, TimestampMixin):
    __tablename__ = "analytics_records"
    __table_args__ = (UniqueConstraint("publishing_task_id", name="uq_analytics_publishing_task"),)

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    publishing_task_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("publishing_tasks.id"), nullable=True, index=True)
    content_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("contents.id"), nullable=True, index=True)
    platform: Mapped[str] = mapped_column(String(64), index=True, default="")
    content_type: Mapped[str] = mapped_column(String(64), index=True, default="")
    stats_date: Mapped[str] = mapped_column(String(32), default="")
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    saves: Mapped[int] = mapped_column(Integer, default=0)
    followers_gained: Mapped[int] = mapped_column(Integer, default=0)
    tracking_status: Mapped[str] = mapped_column(String(64), index=True, default="NOT_STARTED")
    performance_analysis: Mapped[str] = mapped_column(Text, default="")
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    publishing_task: Mapped[PublishingTask | None] = relationship(back_populates="analytics_records")
    content: Mapped[Content | None] = relationship(back_populates="analytics_records")
    tracking_snapshots: Mapped[list["TrackingSnapshot"]] = relationship(back_populates="analytics_record", cascade="all, delete-orphan")
    experience_records: Mapped[list["ExperienceRecord"]] = relationship(back_populates="analytics_record")


class TrackingSnapshot(Base, TimestampMixin):
    __tablename__ = "tracking_snapshots"
    __table_args__ = (
        UniqueConstraint("publishing_task_id", "checkpoint_id", "sequence", name="uq_tracking_checkpoint_sequence"),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    publishing_task_id: Mapped[str] = mapped_column(String(128), ForeignKey("publishing_tasks.id"), index=True)
    analytics_record_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("analytics_records.id"), nullable=True, index=True)
    checkpoint_id: Mapped[str] = mapped_column(String(64), index=True, default="")
    sequence: Mapped[int] = mapped_column(Integer, default=1)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    label: Mapped[str] = mapped_column(String(64), default="")
    due_at: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(64), index=True, default="PENDING")
    stats_date: Mapped[str] = mapped_column(String(32), default="")
    metrics: Mapped[dict] = mapped_column(JsonType, default=dict)
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    publishing_task: Mapped[PublishingTask] = relationship(back_populates="tracking_snapshots")
    analytics_record: Mapped[AnalyticsRecord | None] = relationship(back_populates="tracking_snapshots")


class ExperienceRecord(Base, TimestampMixin):
    __tablename__ = "experience_records"
    __table_args__ = (UniqueConstraint("publishing_task_id", name="uq_experience_publishing_task"),)

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    content_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("contents.id"), nullable=True, index=True)
    topic_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("topics.id"), nullable=True, index=True)
    platform_version_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("platform_versions.id"), nullable=True, index=True)
    publishing_task_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("publishing_tasks.id"), nullable=True, index=True)
    analytics_record_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("analytics_records.id"), nullable=True, index=True)
    platform: Mapped[str] = mapped_column(String(64), index=True, default="")
    content_type: Mapped[str] = mapped_column(String(64), index=True, default="")
    topic_category: Mapped[str] = mapped_column(String(128), index=True, default="")
    performance_result: Mapped[str] = mapped_column(Text, default="")
    effective_practices: Mapped[list] = mapped_column(JsonType, default=list)
    improvements: Mapped[list] = mapped_column(JsonType, default=list)
    review_summary: Mapped[str] = mapped_column(Text, default="")
    reviewed_at: Mapped[str] = mapped_column(String(64), default="")
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    content: Mapped[Content | None] = relationship(back_populates="experience_records")
    topic: Mapped[Topic | None] = relationship()
    platform_version: Mapped[PlatformVersion | None] = relationship(back_populates="experience_records")
    publishing_task: Mapped[PublishingTask | None] = relationship(back_populates="experience_records")
    analytics_record: Mapped[AnalyticsRecord | None] = relationship(back_populates="experience_records")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, default="default")
    action: Mapped[str] = mapped_column(String(64), index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(128), index=True)
    details: Mapped[dict] = mapped_column(JsonType, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True, nullable=False)
