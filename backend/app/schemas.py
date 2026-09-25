from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


JsonDict = dict[str, Any]


class TopicIn(BaseModel):
    id: str
    workspace_id: str = "default"
    source: str = "mock"
    title: str
    url: str = ""
    author: str = ""
    category: str = ""
    status: str = "DISCOVERED"
    score: int = 0
    raw: JsonDict = Field(default_factory=dict)


class TopicOut(TopicIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ContentIn(BaseModel):
    id: str
    workspace_id: str = "default"
    topic_id: str | None = None
    title: str
    status: str = "DRAFT"
    platform: str = ""
    content_type: str = ""
    source_url: str = ""
    revision: int = Field(default=1, ge=1)
    content_hash: str = ""
    raw: JsonDict = Field(default_factory=dict)


class ContentOut(ContentIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class KnowledgeEntryIn(BaseModel):
    id: str
    workspace_id: str = "default"
    topic_id: str | None = None
    content_id: str | None = None
    title: str
    body: str = ""
    knowledge_type: Literal["Fact", "Source / Research", "Inference", "Creator Preference", "Learning", "Playbook"] = "Source / Research"
    source: str = ""
    source_url: str = ""
    tags: list[str] = Field(default_factory=list)
    confidence: int = Field(default=70, ge=0, le=100)
    status: Literal["DRAFT", "ACTIVE", "ARCHIVED"] = "ACTIVE"
    raw: JsonDict = Field(default_factory=dict)


class KnowledgeEntryOut(KnowledgeEntryIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CreatorProfileIn(BaseModel):
    id: str = "default"
    workspace_id: str = "default"
    account_positioning: str = ""
    target_audience: str = ""
    content_pillars: list[str] = Field(default_factory=list)
    tone_style: str = ""
    preferred_formats: list[str] = Field(default_factory=list)
    topics_to_avoid: list[str] = Field(default_factory=list)
    platform_preferences: list[str] = Field(default_factory=list)
    raw: JsonDict = Field(default_factory=dict)


class CreatorProfileOut(CreatorProfileIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ActivityLogOut(BaseModel):
    id: int
    workspace_id: str = "default"
    action: str
    entity_type: str
    entity_id: str
    details: JsonDict = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LocalStorageCoreImportIn(BaseModel):
    topics: list[JsonDict] = Field(default_factory=list)
    contentItems: list[JsonDict] = Field(default_factory=list)
    knowledgeItems: list[JsonDict] = Field(default_factory=list)
    creatorMemory: JsonDict | None = None


class ImportBucketSummary(BaseModel):
    added: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0


class ImportSummary(BaseModel):
    topics: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    contents: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    knowledge: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    creator_memory: ImportBucketSummary = Field(default_factory=ImportBucketSummary)


class PlatformVersionIn(BaseModel):
    id: str
    workspace_id: str = "default"
    content_id: str
    platform: str = ""
    content_type: str = ""
    title: str = ""
    hook: str = ""
    body: str = ""
    tags: list[str] = Field(default_factory=list)
    status: str = "DRAFT"
    revision: int = Field(default=1, ge=1)
    content_hash: str = ""
    is_immutable: bool = False
    raw: JsonDict = Field(default_factory=dict)


class PlatformVersionOut(PlatformVersionIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ApprovalRecordIn(BaseModel):
    id: str
    workspace_id: str = "default"
    content_id: str
    platform_version_id: str | None = None
    platform_version_revision: int = Field(default=0, ge=0)
    snapshot_hash: str = ""
    status: str = "DRAFT"
    notes: str = ""
    reviewed_at: datetime | None = None
    approved_at: datetime | None = None
    invalidated_at: datetime | None = None
    invalidation_reason: str = ""
    snapshot: JsonDict = Field(default_factory=dict)
    raw: JsonDict = Field(default_factory=dict)


class ApprovalRecordOut(ApprovalRecordIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PublishingTaskIn(BaseModel):
    id: str
    workspace_id: str = "default"
    content_id: str
    platform_version_id: str | None = None
    approval_record_id: str | None = None
    content_revision: int = Field(default=1, ge=1)
    version_snapshot: JsonDict = Field(default_factory=dict)
    platform: str = ""
    content_type: str = ""
    scheduled_at: str = ""
    actual_published_at: str = ""
    status: str = "DRAFT"
    url: str = ""
    notes: str = ""
    raw: JsonDict = Field(default_factory=dict)


class PublishingTaskOut(PublishingTaskIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AnalyticsRecordIn(BaseModel):
    id: str
    workspace_id: str = "default"
    publishing_task_id: str | None = None
    content_id: str | None = None
    platform: str = ""
    content_type: str = ""
    stats_date: str = ""
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    followers_gained: int = 0
    tracking_status: str = "NOT_STARTED"
    performance_analysis: str = ""
    raw: JsonDict = Field(default_factory=dict)


class AnalyticsRecordOut(AnalyticsRecordIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TrackingSnapshotIn(BaseModel):
    id: str
    workspace_id: str = "default"
    publishing_task_id: str
    analytics_record_id: str | None = None
    checkpoint_id: str = ""
    sequence: int = Field(default=1, ge=1)
    recorded_at: datetime | None = None
    label: str = ""
    due_at: str = ""
    status: str = "PENDING"
    stats_date: str = ""
    metrics: JsonDict = Field(default_factory=dict)
    raw: JsonDict = Field(default_factory=dict)


class TrackingSnapshotOut(TrackingSnapshotIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ExperienceRecordIn(BaseModel):
    id: str
    workspace_id: str = "default"
    content_id: str | None = None
    topic_id: str | None = None
    platform_version_id: str | None = None
    publishing_task_id: str | None = None
    analytics_record_id: str | None = None
    platform: str = ""
    content_type: str = ""
    topic_category: str = ""
    performance_result: str = ""
    effective_practices: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    review_summary: str = ""
    reviewed_at: str = ""
    raw: JsonDict = Field(default_factory=dict)


class ExperienceRecordOut(ExperienceRecordIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class LocalStorageBusinessImportIn(BaseModel):
    contentItems: list[JsonDict] = Field(default_factory=list)
    generatedAssets: list[JsonDict] = Field(default_factory=list)
    publishJobs: list[JsonDict] = Field(default_factory=list)
    analyticsRecords: list[JsonDict] = Field(default_factory=list)
    experienceItems: list[JsonDict] = Field(default_factory=list)


class BusinessImportSummary(BaseModel):
    platform_versions: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    approvals: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    publishing_tasks: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    tracking_snapshots: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    analytics_records: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    experience_records: ImportBucketSummary = Field(default_factory=ImportBucketSummary)


class MarkdownExportRequest(BaseModel):
    ids: list[str] = Field(default_factory=list)


class MarkdownFile(BaseModel):
    filename: str
    content: str


class MarkdownExportResponse(BaseModel):
    files: list[MarkdownFile]
