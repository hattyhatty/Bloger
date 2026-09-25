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


OpportunityStatus = Literal["candidate", "saved", "rejected", "developed"]


class OpportunityCandidateIn(BaseModel):
    id: str
    summary: str = ""
    why_it_matters: str = ""
    audience: str = ""
    underlying_need_or_emotion: str = ""
    content_opportunity: str
    recommended_format: str = ""
    platform_fit: list[str] = Field(default_factory=list)
    novelty: int = Field(default=0, ge=0, le=100)
    timeliness: int = Field(default=0, ge=0, le=100)
    audience_fit: int = Field(default=0, ge=0, le=100)
    creator_fit: int = Field(default=0, ge=0, le=100)
    human_need_strength: int = Field(default=0, ge=0, le=100)
    platform_fit_score: int = Field(default=0, ge=0, le=100)
    visual_potential: int = Field(default=0, ge=0, le=100)
    production_difficulty: int = Field(default=0, ge=0, le=100)
    overall_score: int = Field(default=0, ge=0, le=100)
    reasoning: str = ""
    raw: JsonDict = Field(default_factory=dict)


class OpportunityAnalysisIn(BaseModel):
    workspace_id: str = "default"
    topic_id: str
    creator_profile_id: str | None = None
    analysis_batch_id: str
    knowledge_ids: list[str] = Field(default_factory=list)
    opportunities: list[OpportunityCandidateIn] = Field(min_length=3, max_length=5)


class ContentOpportunityIn(OpportunityCandidateIn):
    workspace_id: str = "default"
    topic_id: str
    creator_profile_id: str = "default"
    developed_content_id: str | None = None
    analysis_batch_id: str
    angle_key: str = ""
    knowledge_ids: list[str] = Field(default_factory=list)
    learning_ids: list[str] = Field(default_factory=list)
    learning_adjustment: int = Field(default=0, ge=-8, le=8)
    learning_explanation: list[str] = Field(default_factory=list)
    exploration_bonus: int = Field(default=0, ge=0, le=5)
    status: OpportunityStatus = "candidate"


class ContentOpportunityOut(ContentOpportunityIn):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class OpportunityStatusIn(BaseModel):
    workspace_id: str = "default"
    status: Literal["candidate", "saved", "rejected"]


class OpportunityDevelopIn(BaseModel):
    workspace_id: str = "default"
    content_id: str | None = None


class OpportunityDevelopOut(BaseModel):
    opportunity: ContentOpportunityOut
    content: ContentOut


CreatorLearningStatus = Literal["proposed", "active", "weakened", "archived"]


class CreatorLearningEvidenceOut(BaseModel):
    id: str
    workspace_id: str = "default"
    learning_id: str
    content_id: str | None = None
    opportunity_id: str | None = None
    publishing_task_id: str | None = None
    analytics_record_id: str
    experience_record_id: str | None = None
    tracking_snapshot_ids: list[str] = Field(default_factory=list)
    metrics: JsonDict = Field(default_factory=dict)
    observed_at: datetime
    supports: bool = True
    outcome_score: int = Field(default=0, ge=-100, le=100)
    raw: JsonDict = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CreatorLearningOut(BaseModel):
    id: str
    workspace_id: str = "default"
    creator_profile_id: str
    knowledge_entry_id: str | None = None
    pattern_key: str
    learning_statement: str
    learning_type: str
    context_key: str = ""
    direction: str = "neutral"
    supporting_metrics: JsonDict = Field(default_factory=dict)
    sample_size: int = 0
    confidence: int = Field(default=0, ge=0, le=100)
    consistency: int = Field(default=0, ge=0, le=100)
    recency_score: int = Field(default=0, ge=0, le=100)
    effect_strength: int = Field(default=0, ge=0, le=100)
    status: CreatorLearningStatus = "proposed"
    last_validated_at: datetime | None = None
    evidence: list[CreatorLearningEvidenceOut] = Field(default_factory=list)
    raw: JsonDict = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class StrategySuggestionOut(BaseModel):
    id: str
    workspace_id: str = "default"
    creator_profile_id: str
    fingerprint: str
    suggestion_type: str
    statement: str
    proposed_change: JsonDict = Field(default_factory=dict)
    rationale: str = ""
    supporting_learning_ids: list[str] = Field(default_factory=list)
    status: Literal["pending", "accepted", "rejected", "ignored"] = "pending"
    decided_at: datetime | None = None
    raw: JsonDict = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class StrategySuggestionDecisionIn(BaseModel):
    workspace_id: str = "default"
    decision: Literal["accepted", "rejected", "ignored"]


class StrategySuggestionDecisionOut(BaseModel):
    suggestion: StrategySuggestionOut
    creator_memory: CreatorProfileOut


class CreatorIntelligenceGenerateIn(BaseModel):
    workspace_id: str = "default"


class CreatorIntelligenceOut(BaseModel):
    learnings: list[CreatorLearningOut] = Field(default_factory=list)
    strategy_suggestions: list[StrategySuggestionOut] = Field(default_factory=list)
    summary: JsonDict = Field(default_factory=dict)


class OpportunityContextOut(BaseModel):
    topic: TopicOut
    knowledge: list[KnowledgeEntryOut] = Field(default_factory=list)
    creator_memory: CreatorProfileOut
    learnings: list[CreatorLearningOut] = Field(default_factory=list)


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
    opportunityItems: list[JsonDict] = Field(default_factory=list)
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
    opportunities: ImportBucketSummary = Field(default_factory=ImportBucketSummary)


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
    creatorLearnings: list[JsonDict] = Field(default_factory=list)
    strategySuggestions: list[JsonDict] = Field(default_factory=list)


class BusinessImportSummary(BaseModel):
    platform_versions: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    approvals: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    publishing_tasks: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    tracking_snapshots: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    analytics_records: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    experience_records: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    creator_learnings: ImportBucketSummary = Field(default_factory=ImportBucketSummary)
    strategy_suggestions: ImportBucketSummary = Field(default_factory=ImportBucketSummary)


class MarkdownExportRequest(BaseModel):
    ids: list[str] = Field(default_factory=list)


class MarkdownFile(BaseModel):
    filename: str
    content: str


class MarkdownExportResponse(BaseModel):
    files: list[MarkdownFile]
