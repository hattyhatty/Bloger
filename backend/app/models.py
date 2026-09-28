from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, Column, JSON, DateTime, ForeignKey, Index, Integer, String, Table, Text, UniqueConstraint, text
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

opportunity_learning_links = Table(
    "opportunity_learning_links",
    Base.metadata,
    Column("opportunity_id", String(128), ForeignKey("content_opportunities.id", ondelete="CASCADE"), primary_key=True),
    Column("creator_learning_id", String(128), ForeignKey("creator_learnings.id"), primary_key=True),
)
Index("ix_opportunity_learning_links_creator_learning_id", opportunity_learning_links.c.creator_learning_id)


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
    video_production_plans: Mapped[list["VideoProductionPlan"]] = relationship(back_populates="content", cascade="all, delete-orphan")


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
    creator_learnings: Mapped[list["CreatorLearning"]] = relationship(back_populates="creator_profile")
    strategy_suggestions: Mapped[list["StrategySuggestion"]] = relationship(back_populates="creator_profile")


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
        CheckConstraint("learning_adjustment BETWEEN -8 AND 8", name="ck_opportunity_learning_adjustment"),
        CheckConstraint("exploration_bonus BETWEEN 0 AND 5", name="ck_opportunity_exploration_bonus"),
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
    learning_adjustment: Mapped[int] = mapped_column(Integer, default=0)
    learning_explanation: Mapped[list] = mapped_column(JsonType, default=list)
    exploration_bonus: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), index=True, default="candidate")
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    topic: Mapped[Topic] = relationship(back_populates="opportunities")
    creator_profile: Mapped[CreatorProfile] = relationship(back_populates="opportunities")
    developed_content: Mapped[Content | None] = relationship(back_populates="developed_opportunities")
    relevant_knowledge: Mapped[list[KnowledgeEntry]] = relationship(
        secondary=opportunity_knowledge_links,
        back_populates="opportunities",
    )
    relevant_learnings: Mapped[list["CreatorLearning"]] = relationship(
        secondary=opportunity_learning_links,
        back_populates="opportunities",
    )

    @property
    def knowledge_ids(self) -> list[str]:
        return [item.id for item in self.relevant_knowledge]

    @property
    def learning_ids(self) -> list[str]:
        return [item.id for item in self.relevant_learnings]


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


class CreatorLearning(Base, TimestampMixin):
    __tablename__ = "creator_learnings"
    __table_args__ = (
        UniqueConstraint("workspace_id", "pattern_key", name="uq_creator_learning_pattern"),
        CheckConstraint("status IN ('proposed', 'active', 'weakened', 'archived')", name="ck_creator_learning_status"),
        CheckConstraint("confidence BETWEEN 0 AND 100", name="ck_creator_learning_confidence"),
        CheckConstraint("consistency BETWEEN 0 AND 100", name="ck_creator_learning_consistency"),
        CheckConstraint("recency_score BETWEEN 0 AND 100", name="ck_creator_learning_recency"),
        CheckConstraint("effect_strength BETWEEN 0 AND 100", name="ck_creator_learning_effect"),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    creator_profile_id: Mapped[str] = mapped_column(String(128), ForeignKey("creator_profiles.id"), index=True)
    knowledge_entry_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("knowledge_entries.id"), nullable=True, index=True)
    pattern_key: Mapped[str] = mapped_column(String(255), index=True)
    learning_statement: Mapped[str] = mapped_column(Text)
    learning_type: Mapped[str] = mapped_column(String(64), index=True)
    context_key: Mapped[str] = mapped_column(String(255), index=True, default="")
    direction: Mapped[str] = mapped_column(String(32), default="neutral")
    supporting_metrics: Mapped[dict] = mapped_column(JsonType, default=dict)
    sample_size: Mapped[int] = mapped_column(Integer, default=0)
    confidence: Mapped[int] = mapped_column(Integer, default=0)
    consistency: Mapped[int] = mapped_column(Integer, default=0)
    recency_score: Mapped[int] = mapped_column(Integer, default=0)
    effect_strength: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), index=True, default="proposed")
    last_validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    creator_profile: Mapped[CreatorProfile] = relationship(back_populates="creator_learnings")
    knowledge_entry: Mapped[KnowledgeEntry | None] = relationship()
    evidence: Mapped[list["CreatorLearningEvidence"]] = relationship(back_populates="learning", cascade="all, delete-orphan")
    opportunities: Mapped[list[ContentOpportunity]] = relationship(
        secondary=opportunity_learning_links,
        back_populates="relevant_learnings",
    )


class CreatorLearningEvidence(Base, TimestampMixin):
    __tablename__ = "creator_learning_evidence"
    __table_args__ = (
        UniqueConstraint("learning_id", "analytics_record_id", name="uq_learning_analytics_evidence"),
        CheckConstraint("outcome_score BETWEEN -100 AND 100", name="ck_learning_evidence_outcome"),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    learning_id: Mapped[str] = mapped_column(String(128), ForeignKey("creator_learnings.id", ondelete="CASCADE"), index=True)
    content_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("contents.id"), nullable=True, index=True)
    opportunity_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("content_opportunities.id"), nullable=True, index=True)
    publishing_task_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("publishing_tasks.id"), nullable=True, index=True)
    analytics_record_id: Mapped[str] = mapped_column(String(128), ForeignKey("analytics_records.id"), index=True)
    experience_record_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("experience_records.id"), nullable=True, index=True)
    tracking_snapshot_ids: Mapped[list] = mapped_column(JsonType, default=list)
    metrics: Mapped[dict] = mapped_column(JsonType, default=dict)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    supports: Mapped[bool] = mapped_column(Boolean, default=True)
    outcome_score: Mapped[int] = mapped_column(Integer, default=0)
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    learning: Mapped[CreatorLearning] = relationship(back_populates="evidence")


class StrategySuggestion(Base, TimestampMixin):
    __tablename__ = "strategy_suggestions"
    __table_args__ = (
        UniqueConstraint("workspace_id", "fingerprint", name="uq_strategy_suggestion_fingerprint"),
        CheckConstraint("status IN ('pending', 'accepted', 'rejected', 'ignored')", name="ck_strategy_suggestion_status"),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    creator_profile_id: Mapped[str] = mapped_column(String(128), ForeignKey("creator_profiles.id"), index=True)
    fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    suggestion_type: Mapped[str] = mapped_column(String(64), index=True)
    statement: Mapped[str] = mapped_column(Text)
    proposed_change: Mapped[dict] = mapped_column(JsonType, default=dict)
    rationale: Mapped[str] = mapped_column(Text, default="")
    supporting_learning_ids: Mapped[list] = mapped_column(JsonType, default=list)
    status: Mapped[str] = mapped_column(String(32), index=True, default="pending")
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    creator_profile: Mapped[CreatorProfile] = relationship(back_populates="strategy_suggestions")


class VideoProductionPlan(Base, TimestampMixin):
    __tablename__ = "video_production_plans"
    __table_args__ = (
        UniqueConstraint("workspace_id", "content_id", "content_revision", name="uq_video_plan_content_revision"),
        CheckConstraint("status IN ('draft', 'planned', 'in_production', 'ready_for_review')", name="ck_video_plan_status"),
        CheckConstraint("target_duration_seconds BETWEEN 1 AND 14400", name="ck_video_plan_duration"),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    content_id: Mapped[str] = mapped_column(String(128), ForeignKey("contents.id"), index=True)
    opportunity_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("content_opportunities.id"), nullable=True, index=True)
    content_revision: Mapped[int] = mapped_column(Integer)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, default="")
    content_snapshot: Mapped[dict] = mapped_column(JsonType, default=dict)
    video_concept: Mapped[str] = mapped_column(Text, default="")
    target_platform: Mapped[str] = mapped_column(String(64), index=True, default="抖音")
    target_duration_seconds: Mapped[int] = mapped_column(Integer, default=60)
    content_format: Mapped[str] = mapped_column(String(128), default="口播")
    visual_style: Mapped[str] = mapped_column(Text, default="")
    aspect_ratio: Mapped[str] = mapped_column(String(32), default="9:16")
    status: Mapped[str] = mapped_column(String(32), index=True, default="draft")
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    content: Mapped[Content] = relationship(back_populates="video_production_plans")
    opportunity: Mapped[ContentOpportunity | None] = relationship()
    script: Mapped["VideoScript | None"] = relationship(back_populates="plan", cascade="all, delete-orphan", uselist=False)
    storyboard: Mapped["VideoStoryboard | None"] = relationship(back_populates="plan", cascade="all, delete-orphan", uselist=False)

    @property
    def content_changed(self) -> bool:
        return bool(self.content and (self.content.revision != self.content_revision or (self.content_hash and self.content.content_hash != self.content_hash)))


class VideoScript(Base, TimestampMixin):
    __tablename__ = "video_scripts"
    __table_args__ = (UniqueConstraint("plan_id", name="uq_video_script_plan"),)

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    plan_id: Mapped[str] = mapped_column(String(128), ForeignKey("video_production_plans.id", ondelete="CASCADE"), index=True)
    hook: Mapped[str] = mapped_column(Text, default="")
    narration_dialogue: Mapped[str] = mapped_column(Text, default="")
    main_story_flow: Mapped[str] = mapped_column(Text, default="")
    ending_cta: Mapped[str] = mapped_column(Text, default="")
    estimated_duration_seconds: Mapped[int] = mapped_column(Integer, default=60)
    source_context: Mapped[dict] = mapped_column(JsonType, default=dict)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    plan: Mapped[VideoProductionPlan] = relationship(back_populates="script")
    storyboards: Mapped[list["VideoStoryboard"]] = relationship(back_populates="script")


class VideoStoryboard(Base, TimestampMixin):
    __tablename__ = "video_storyboards"
    __table_args__ = (UniqueConstraint("plan_id", name="uq_video_storyboard_plan"),)

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    plan_id: Mapped[str] = mapped_column(String(128), ForeignKey("video_production_plans.id", ondelete="CASCADE"), index=True)
    script_id: Mapped[str] = mapped_column(String(128), ForeignKey("video_scripts.id"), index=True)
    recurring_character_description: Mapped[str] = mapped_column(Text, default="")
    clothing: Mapped[str] = mapped_column(Text, default="")
    environment: Mapped[str] = mapped_column(Text, default="")
    visual_style: Mapped[str] = mapped_column(Text, default="")
    reference_notes: Mapped[str] = mapped_column(Text, default="")
    revision: Mapped[int] = mapped_column(Integer, default=1)
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    plan: Mapped[VideoProductionPlan] = relationship(back_populates="storyboard")
    script: Mapped[VideoScript] = relationship(back_populates="storyboards")
    shots: Mapped[list["VideoShot"]] = relationship(back_populates="storyboard", cascade="all, delete-orphan", order_by="VideoShot.shot_number")


class VideoShot(Base, TimestampMixin):
    __tablename__ = "video_shots"
    __table_args__ = (
        UniqueConstraint("storyboard_id", "shot_number", name="uq_video_shot_number"),
        CheckConstraint("shot_number >= 1", name="ck_video_shot_number"),
        CheckConstraint("estimated_duration_seconds BETWEEN 1 AND 3600", name="ck_video_shot_duration"),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    storyboard_id: Mapped[str] = mapped_column(String(128), ForeignKey("video_storyboards.id", ondelete="CASCADE"), index=True)
    shot_number: Mapped[int] = mapped_column(Integer)
    estimated_duration_seconds: Mapped[int] = mapped_column(Integer, default=5)
    scene_description: Mapped[str] = mapped_column(Text, default="")
    subject_character: Mapped[str] = mapped_column(Text, default="")
    action: Mapped[str] = mapped_column(Text, default="")
    environment: Mapped[str] = mapped_column(Text, default="")
    camera_framing: Mapped[str] = mapped_column(String(128), default="")
    camera_movement: Mapped[str] = mapped_column(String(128), default="")
    lighting_mood: Mapped[str] = mapped_column(Text, default="")
    narration_dialogue: Mapped[str] = mapped_column(Text, default="")
    transition: Mapped[str] = mapped_column(String(128), default="")
    generation_notes: Mapped[str] = mapped_column(Text, default="")
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    storyboard: Mapped[VideoStoryboard] = relationship(back_populates="shots")
    prompts: Mapped[list["VideoGenerationPrompt"]] = relationship(back_populates="shot", cascade="all, delete-orphan")
    reference_links: Mapped[list["VideoShotReferenceLink"]] = relationship(back_populates="shot", cascade="all, delete-orphan")
    generation_results: Mapped[list["VideoGenerationResult"]] = relationship(back_populates="shot")


class VideoGenerationPrompt(Base, TimestampMixin):
    __tablename__ = "video_generation_prompts"
    __table_args__ = (
        UniqueConstraint("shot_id", "prompt_target", name="uq_video_prompt_shot_target"),
        CheckConstraint("prompt_target IN ('Generic', 'Seedance', 'Kling', 'Veo', 'Runway')", name="ck_video_prompt_target"),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    shot_id: Mapped[str] = mapped_column(String(128), ForeignKey("video_shots.id", ondelete="CASCADE"), index=True)
    prompt_target: Mapped[str] = mapped_column(String(32), index=True, default="Generic")
    generic_video_prompt: Mapped[str] = mapped_column(Text, default="")
    image_reference_prompt: Mapped[str] = mapped_column(Text, default="")
    negative_instructions: Mapped[str] = mapped_column(Text, default="")
    continuity_notes: Mapped[str] = mapped_column(Text, default="")
    source_shot_hash: Mapped[str] = mapped_column(String(64), index=True, default="")
    revision: Mapped[int] = mapped_column(Integer, default=1)
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    shot: Mapped[VideoShot] = relationship(back_populates="prompts")


class VideoReferenceAsset(Base, TimestampMixin):
    __tablename__ = "video_reference_assets"
    __table_args__ = (
        CheckConstraint(
            "asset_type IN ('character', 'clothing', 'environment', 'style', 'other')",
            name="ck_video_reference_asset_type",
        ),
        CheckConstraint("status IN ('active', 'archived')", name="ck_video_reference_asset_status"),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    asset_type: Mapped[str] = mapped_column(String(32), index=True, default="other")
    title: Mapped[str] = mapped_column(String(255), default="")
    reference_url: Mapped[str] = mapped_column(Text, default="")
    file_reference: Mapped[str] = mapped_column(Text, default="")
    note: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), index=True, default="active")
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    shot_links: Mapped[list["VideoShotReferenceLink"]] = relationship(back_populates="asset", cascade="all, delete-orphan")


class VideoShotReferenceLink(Base, TimestampMixin):
    __tablename__ = "video_shot_reference_links"
    __table_args__ = (UniqueConstraint("shot_id", "asset_id", name="uq_video_shot_reference_link"),)

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    shot_id: Mapped[str] = mapped_column(String(128), ForeignKey("video_shots.id", ondelete="CASCADE"), index=True)
    asset_id: Mapped[str] = mapped_column(String(128), ForeignKey("video_reference_assets.id"), index=True)
    plan_id: Mapped[str] = mapped_column(String(128), ForeignKey("video_production_plans.id"), index=True)
    plan_content_revision: Mapped[int] = mapped_column(Integer)

    shot: Mapped[VideoShot] = relationship(back_populates="reference_links")
    asset: Mapped[VideoReferenceAsset] = relationship(back_populates="shot_links")


class VideoGenerationResult(Base, TimestampMixin):
    __tablename__ = "video_generation_results"
    __table_args__ = (
        CheckConstraint(
            "status IN ('candidate', 'selected', 'rejected', 'archived')",
            name="ck_video_generation_result_status",
        ),
        Index(
            "uq_video_generation_result_selected_shot",
            "shot_id",
            unique=True,
            postgresql_where=text("status = 'selected'"),
            sqlite_where=text("status = 'selected'"),
        ),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(128), ForeignKey("workspaces.id"), index=True, default="default")
    plan_id: Mapped[str] = mapped_column(String(128), ForeignKey("video_production_plans.id"), index=True)
    shot_id: Mapped[str] = mapped_column(String(128), ForeignKey("video_shots.id"), index=True)
    prompt_id: Mapped[str] = mapped_column(String(128), ForeignKey("video_generation_prompts.id"), index=True)
    plan_content_revision: Mapped[int] = mapped_column(Integer)
    storyboard_revision: Mapped[int] = mapped_column(Integer)
    prompt_revision: Mapped[int] = mapped_column(Integer)
    shot_snapshot: Mapped[dict] = mapped_column(JsonType, default=dict)
    prompt_snapshot: Mapped[dict] = mapped_column(JsonType, default=dict)
    provider: Mapped[str] = mapped_column(String(64), index=True, default="External")
    model: Mapped[str] = mapped_column(String(128), default="")
    result_url: Mapped[str] = mapped_column(Text, default="")
    file_reference: Mapped[str] = mapped_column(Text, default="")
    note: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), index=True, default="candidate")
    raw: Mapped[dict] = mapped_column(JsonType, default=dict)

    shot: Mapped[VideoShot] = relationship(back_populates="generation_results")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, default="default")
    action: Mapped[str] = mapped_column(String(64), index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(128), index=True)
    details: Mapped[dict] = mapped_column(JsonType, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True, nullable=False)
