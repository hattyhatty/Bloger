from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, Column, JSON, DateTime, ForeignKey, Index, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

JsonType = JSON().with_variant(JSONB, "postgresql")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


opportunity_knowledge_links = Table(
    "opportunity_knowledge_links",
    Base.metadata,
    Column("opportunity_id", String(128), ForeignKey("content_opportunities.id", ondelete="CASCADE"), primary_key=True),
    Column("knowledge_entry_id", String(128), ForeignKey("knowledge_entries.id"), primary_key=True),
)
Index("ix_opportunity_knowledge_links_knowledge_entry_id", opportunity_knowledge_links.c.knowledge_entry_id)


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
    opportunities: Mapped[list["ContentOpportunity"]] = relationship(back_populates="topic")


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
    developed_opportunities: Mapped[list["ContentOpportunity"]] = relationship(back_populates="developed_content")


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
    opportunities: Mapped[list["ContentOpportunity"]] = relationship(
        secondary=opportunity_knowledge_links,
        back_populates="relevant_knowledge",
    )


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

    opportunities: Mapped[list["ContentOpportunity"]] = relationship(back_populates="creator_profile")


class ContentOpportunity(Base, TimestampMixin):
    __tablename__ = "content_opportunities"
    __table_args__ = (
        UniqueConstraint("workspace_id", "topic_id", "analysis_batch_id", "angle_key", name="uq_opportunity_batch_angle"),
        UniqueConstraint("developed_content_id", name="uq_opportunity_developed_content"),
        CheckConstraint("status IN ('candidate', 'saved', 'rejected', 'developed')", name="ck_opportunity_status"),
        CheckConstraint(
            "novelty BETWEEN 0 AND 100 AND timeliness BETWEEN 0 AND 100 "
            "AND audience_fit BETWEEN 0 AND 100 AND creator_fit BETWEEN 0 AND 100 "
            "AND human_need_strength BETWEEN 0 AND 100 AND platform_fit_score BETWEEN 0 AND 100 "
            "AND visual_potential BETWEEN 0 AND 100 AND production_difficulty BETWEEN 0 AND 100 "
            "AND overall_score BETWEEN 0 AND 100",
            name="ck_opportunity_scores",
        ),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    topic_id: Mapped[str] = mapped_column(String(128), ForeignKey("topics.id"), index=True)
    creator_profile_id: Mapped[str] = mapped_column(String(128), ForeignKey("creator_profiles.id"), index=True)
    developed_content_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("contents.id"), nullable=True, index=True)
    analysis_batch_id: Mapped[str] = mapped_column(String(128), index=True)
    angle_key: Mapped[str] = mapped_column(String(64), index=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    why_it_matters: Mapped[str] = mapped_column(Text, default="")
    audience: Mapped[str] = mapped_column(Text, default="")
    underlying_need_or_emotion: Mapped[str] = mapped_column(Text, default="")
    content_opportunity: Mapped[str] = mapped_column(Text)
    recommended_format: Mapped[str] = mapped_column(String(128), default="")
    platform_fit: Mapped[list] = mapped_column(JsonType, default=list)
    novelty: Mapped[int] = mapped_column(Integer, default=0)
    timeliness: Mapped[int] = mapped_column(Integer, default=0)
    audience_fit: Mapped[int] = mapped_column(Integer, default=0)
    creator_fit: Mapped[int] = mapped_column(Integer, default=0)
    human_need_strength: Mapped[int] = mapped_column(Integer, default=0)
    platform_fit_score: Mapped[int] = mapped_column(Integer, default=0)
    visual_potential: Mapped[int] = mapped_column(Integer, default=0)
    production_difficulty: Mapped[int] = mapped_column(Integer, default=0)
    overall_score: Mapped[int] = mapped_column(Integer, index=True, default=0)
    reasoning: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), index=True, default="candidate")
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    topic: Mapped[Topic] = relationship(back_populates="opportunities")
    creator_profile: Mapped[CreatorProfile] = relationship(back_populates="opportunities")
    developed_content: Mapped[Content | None] = relationship(back_populates="developed_opportunities")
    relevant_knowledge: Mapped[list[KnowledgeEntry]] = relationship(
        secondary=opportunity_knowledge_links,
        back_populates="opportunities",
    )

    @property
    def knowledge_ids(self) -> list[str]:
        return [item.id for item in self.relevant_knowledge]


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
