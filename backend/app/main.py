import json
from datetime import datetime, timezone
from typing import Any, TypeVar

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from .activity import log_activity
from .config import get_settings
from .database import get_db
from .models import (
    ActivityLog,
    AnalyticsRecord,
    ApprovalRecord,
    Content,
    ContentOpportunity,
    CreatorProfile,
    ExperienceRecord,
    KnowledgeEntry,
    PlatformVersion,
    PublishingTask,
    Topic,
    TrackingSnapshot,
    Workspace,
)
from .obsidian import knowledge_to_markdown, safe_filename
from .schemas import (
    ActivityLogOut,
    AnalyticsRecordIn,
    AnalyticsRecordOut,
    ApprovalRecordIn,
    ApprovalRecordOut,
    BusinessImportSummary,
    ContentIn,
    ContentOut,
    ContentOpportunityIn,
    ContentOpportunityOut,
    CreatorProfileIn,
    CreatorProfileOut,
    ExperienceRecordIn,
    ExperienceRecordOut,
    ImportBucketSummary,
    ImportSummary,
    KnowledgeEntryIn,
    KnowledgeEntryOut,
    LocalStorageBusinessImportIn,
    LocalStorageCoreImportIn,
    MarkdownExportRequest,
    MarkdownExportResponse,
    MarkdownFile,
    OpportunityAnalysisIn,
    OpportunityContextOut,
    OpportunityDevelopIn,
    OpportunityDevelopOut,
    OpportunityStatusIn,
    PlatformVersionIn,
    PlatformVersionOut,
    PublishingTaskIn,
    PublishingTaskOut,
    TopicIn,
    TopicOut,
    TrackingSnapshotIn,
    TrackingSnapshotOut,
)
from .opportunity import (
    analyze_opportunities,
    develop_opportunity,
    import_opportunity_record,
    retrieve_opportunity_context,
    update_opportunity_status,
)
from .workflow import (
    DEFAULT_WORKSPACE_ID,
    WorkflowConflict,
    append_tracking_snapshot,
    assert_knowledge_type_boundary,
    canonical_status,
    ensure_workspace,
    save_analytics,
    save_approval as save_approval_record,
    save_content,
    save_experience,
    save_platform_version as save_platform_version_record,
    save_publishing_task as save_publishing_task_record,
    start_tracking,
    stable_hash,
    validate_knowledge_links,
)


settings = get_settings()
app = FastAPI(title="AI Content OS Backend", version="0.7.3")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ModelT = TypeVar("ModelT")


@app.exception_handler(WorkflowConflict)
async def workflow_conflict_handler(_: Request, error: WorkflowConflict):
    return JSONResponse(status_code=409, content={"detail": str(error)})


@app.get("/api/health")
def api_health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-content-os-backend", "phase": "7E", "sourceOfTruth": "postgresql"}


@app.get("/health")
def health_alias() -> dict[str, str]:
    return api_health()


def list_records(db: Session, statement: Select, limit: int, offset: int) -> list[Any]:
    return list(db.scalars(statement.limit(limit).offset(offset)).all())


def normalize_for_compare(value: Any) -> Any:
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value.isoformat(timespec="seconds")
    if isinstance(value, dict):
        return {key: normalize_for_compare(nested) for key, nested in value.items()}
    if isinstance(value, list):
        return [normalize_for_compare(item) for item in value]
    return value


def comparable_values(values: dict[str, Any]) -> str:
    return json.dumps(normalize_for_compare(values), sort_keys=True, default=str, ensure_ascii=False)


def upsert(
    db: Session,
    model: type[ModelT],
    record_id: str,
    values: dict[str, Any],
    entity_type: str,
    *,
    create_action: str = "create",
    update_action: str = "update",
    commit: bool = True,
) -> tuple[ModelT, bool, bool]:
    existing = db.get(model, record_id)
    created = existing is None
    changed = True
    if existing:
        current = {key: getattr(existing, key) for key in values.keys()}
        changed = comparable_values(current) != comparable_values(values)
        for key, value in values.items():
            setattr(existing, key, value)
        item = existing
    else:
        item = model(id=record_id, **values)
        db.add(item)
    if created or changed:
        log_activity(
            db,
            create_action if created else update_action,
            entity_type,
            record_id,
            {"fields": sorted(values.keys())},
            workspace_id=values.get("workspace_id", DEFAULT_WORKSPACE_ID),
        )
    db.flush()
    if commit:
        db.commit()
        db.refresh(item)
    return item, created, changed


@app.get("/api/topics", response_model=list[TopicOut])
def list_topics(workspace_id: str = DEFAULT_WORKSPACE_ID, limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(Topic).where(Topic.workspace_id == workspace_id).order_by(Topic.updated_at.desc()), limit, offset)


@app.post("/api/topics", response_model=TopicOut)
def create_topic(payload: TopicIn, db: Session = Depends(get_db)):
    ensure_workspace(db, payload.workspace_id)
    item, _, _ = upsert(db, Topic, payload.id, payload.model_dump(exclude={"id"}), "Topic")
    return item


@app.put("/api/topics/{topic_id}", response_model=TopicOut)
def update_topic(topic_id: str, payload: TopicIn, db: Session = Depends(get_db)):
    existing = db.get(Topic, topic_id)
    if existing and existing.workspace_id != payload.workspace_id:
        raise WorkflowConflict("Topic belongs to another workspace")
    ensure_workspace(db, payload.workspace_id)
    values = payload.model_dump(exclude={"id"})
    item, _, _ = upsert(db, Topic, topic_id, values, "Topic")
    return item


@app.get("/api/contents", response_model=list[ContentOut])
def list_contents(workspace_id: str = DEFAULT_WORKSPACE_ID, limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(Content).where(Content.workspace_id == workspace_id).order_by(Content.updated_at.desc()), limit, offset)


@app.post("/api/contents", response_model=ContentOut)
def create_content(payload: ContentIn, db: Session = Depends(get_db)):
    return save_content(db, payload.id, payload.model_dump(exclude={"id"}))


@app.put("/api/contents/{content_id}", response_model=ContentOut)
def update_content(content_id: str, payload: ContentIn, db: Session = Depends(get_db)):
    return save_content(db, content_id, payload.model_dump(exclude={"id"}))


@app.get("/api/knowledge", response_model=list[KnowledgeEntryOut])
def list_knowledge(
    workspace_id: str = DEFAULT_WORKSPACE_ID,
    q: str = "",
    knowledge_type: str = Query("", alias="type"),
    tag: str = "",
    status: str = "",
    source: str = "",
    topic_id: str = "",
    content_id: str = "",
    limit: int = Query(100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    statement = select(KnowledgeEntry).where(KnowledgeEntry.workspace_id == workspace_id)
    if q.strip():
        pattern = f"%{q.strip()}%"
        statement = statement.where(or_(KnowledgeEntry.title.ilike(pattern), KnowledgeEntry.body.ilike(pattern), KnowledgeEntry.source.ilike(pattern)))
    if knowledge_type:
        statement = statement.where(KnowledgeEntry.knowledge_type == knowledge_type)
    if status:
        statement = statement.where(KnowledgeEntry.status == status)
    if source:
        statement = statement.where(KnowledgeEntry.source.ilike(f"%{source.strip()}%"))
    if topic_id:
        statement = statement.where(KnowledgeEntry.topic_id == topic_id)
    if content_id:
        statement = statement.where(KnowledgeEntry.content_id == content_id)
    items = list(db.scalars(statement.order_by(KnowledgeEntry.updated_at.desc())).all())
    if tag.strip():
        expected = tag.strip().casefold()
        items = [item for item in items if any(str(value).casefold() == expected for value in (item.tags or []))]
    return items[offset:offset + limit]


@app.post("/api/knowledge", response_model=KnowledgeEntryOut)
def create_knowledge(payload: KnowledgeEntryIn, db: Session = Depends(get_db)):
    values = payload.model_dump(exclude={"id"})
    validate_knowledge_links(db, values)
    item, _, _ = upsert(
        db,
        KnowledgeEntry,
        payload.id,
        values,
        "KnowledgeEntry",
        create_action="knowledge_created",
        update_action="knowledge_updated",
        commit=False,
    )
    assert_knowledge_type_boundary(item)
    db.commit()
    db.refresh(item)
    return item


@app.put("/api/knowledge/{knowledge_id}", response_model=KnowledgeEntryOut)
def update_knowledge(knowledge_id: str, payload: KnowledgeEntryIn, db: Session = Depends(get_db)):
    values = payload.model_dump(exclude={"id"})
    validate_knowledge_links(db, values)
    item, _, _ = upsert(
        db,
        KnowledgeEntry,
        knowledge_id,
        values,
        "KnowledgeEntry",
        create_action="knowledge_created",
        update_action="knowledge_updated",
        commit=False,
    )
    assert_knowledge_type_boundary(item)
    db.commit()
    db.refresh(item)
    return item


@app.post("/api/knowledge/{knowledge_id}/archive", response_model=KnowledgeEntryOut)
def archive_knowledge(knowledge_id: str, workspace_id: str = DEFAULT_WORKSPACE_ID, db: Session = Depends(get_db)):
    item = db.get(KnowledgeEntry, knowledge_id)
    if not item or item.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    if item.status != "ARCHIVED":
        item.status = "ARCHIVED"
        log_activity(db, "knowledge_archived", "KnowledgeEntry", knowledge_id, {}, workspace_id=workspace_id)
        db.commit()
        db.refresh(item)
    return item


@app.delete("/api/knowledge/{knowledge_id}")
def delete_knowledge(knowledge_id: str, workspace_id: str = DEFAULT_WORKSPACE_ID, db: Session = Depends(get_db)):
    item = db.get(KnowledgeEntry, knowledge_id)
    if not item or item.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    if item.status != "ARCHIVED":
        item.status = "ARCHIVED"
        log_activity(db, "knowledge_archived", "KnowledgeEntry", knowledge_id, {"requestedVia": "DELETE"}, workspace_id=workspace_id)
        db.commit()
    return {"ok": True, "archived": True}


@app.get("/api/creator-memory", response_model=CreatorProfileOut | None)
def get_creator_memory(workspace_id: str = DEFAULT_WORKSPACE_ID, db: Session = Depends(get_db)):
    return db.scalar(select(CreatorProfile).where(CreatorProfile.workspace_id == workspace_id))


@app.put("/api/creator-memory", response_model=CreatorProfileOut)
def update_creator_memory(payload: CreatorProfileIn, db: Session = Depends(get_db)):
    ensure_workspace(db, payload.workspace_id)
    existing = db.scalar(select(CreatorProfile).where(CreatorProfile.workspace_id == payload.workspace_id))
    item, _, _ = upsert(
        db,
        CreatorProfile,
        existing.id if existing else ("default" if payload.workspace_id == DEFAULT_WORKSPACE_ID else f"creator_{payload.workspace_id}"),
        payload.model_dump(exclude={"id"}),
        "CreatorProfile",
        create_action="creator_memory_updated",
        update_action="creator_memory_updated",
    )
    return item


@app.get("/api/topics/{topic_id}/opportunity-context", response_model=OpportunityContextOut)
def get_opportunity_context(
    topic_id: str,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
    limit: int = Query(12, ge=1, le=30),
    db: Session = Depends(get_db),
):
    topic, knowledge, creator = retrieve_opportunity_context(db, topic_id, workspace_id, limit)
    # The single-creator profile is initialized lazily for older databases.
    db.commit()
    return {"topic": topic, "knowledge": knowledge, "creator_memory": creator}


@app.get("/api/opportunities", response_model=list[ContentOpportunityOut])
def list_opportunities(
    workspace_id: str = DEFAULT_WORKSPACE_ID,
    topic_id: str = "",
    status: str = "",
    limit: int = Query(100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    statement = select(ContentOpportunity).where(ContentOpportunity.workspace_id == workspace_id)
    if topic_id:
        statement = statement.where(ContentOpportunity.topic_id == topic_id)
    if status:
        statement = statement.where(ContentOpportunity.status == status.casefold())
    return list_records(
        db,
        statement.order_by(ContentOpportunity.overall_score.desc(), ContentOpportunity.updated_at.desc()),
        limit,
        offset,
    )


@app.post("/api/opportunities/analyze", response_model=list[ContentOpportunityOut])
def save_opportunity_analysis(payload: OpportunityAnalysisIn, db: Session = Depends(get_db)):
    return analyze_opportunities(
        db,
        workspace_id=payload.workspace_id,
        topic_id=payload.topic_id,
        creator_profile_id=payload.creator_profile_id,
        analysis_batch_id=payload.analysis_batch_id,
        knowledge_ids=payload.knowledge_ids,
        candidates=[candidate.model_dump() for candidate in payload.opportunities],
    )


@app.patch("/api/opportunities/{opportunity_id}/status", response_model=ContentOpportunityOut)
def set_opportunity_status(opportunity_id: str, payload: OpportunityStatusIn, db: Session = Depends(get_db)):
    return update_opportunity_status(db, opportunity_id, payload.workspace_id, payload.status)


@app.post("/api/opportunities/{opportunity_id}/develop", response_model=OpportunityDevelopOut)
def develop_saved_opportunity(opportunity_id: str, payload: OpportunityDevelopIn, db: Session = Depends(get_db)):
    opportunity, content = develop_opportunity(db, opportunity_id, payload.workspace_id, payload.content_id)
    return {"opportunity": opportunity, "content": content}


@app.get("/api/activity-logs", response_model=list[ActivityLogOut])
def list_activity_logs(workspace_id: str = DEFAULT_WORKSPACE_ID, limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(ActivityLog).where(ActivityLog.workspace_id == workspace_id).order_by(ActivityLog.created_at.desc()), limit, offset)


@app.get("/api/platform-versions", response_model=list[PlatformVersionOut])
def list_platform_versions(workspace_id: str = DEFAULT_WORKSPACE_ID, limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(PlatformVersion).where(PlatformVersion.workspace_id == workspace_id).order_by(PlatformVersion.updated_at.desc()), limit, offset)


@app.post("/api/platform-versions", response_model=PlatformVersionOut)
def save_platform_version(payload: PlatformVersionIn, db: Session = Depends(get_db)):
    return save_platform_version_record(db, payload.id, payload.model_dump(exclude={"id"}))


@app.put("/api/platform-versions/{record_id}", response_model=PlatformVersionOut)
def update_platform_version(record_id: str, payload: PlatformVersionIn, db: Session = Depends(get_db)):
    return save_platform_version_record(db, record_id, payload.model_dump(exclude={"id"}))


@app.get("/api/approvals", response_model=list[ApprovalRecordOut])
def list_approvals(workspace_id: str = DEFAULT_WORKSPACE_ID, limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(ApprovalRecord).where(ApprovalRecord.workspace_id == workspace_id).order_by(ApprovalRecord.updated_at.desc()), limit, offset)


@app.post("/api/approvals", response_model=ApprovalRecordOut)
def save_approval(payload: ApprovalRecordIn, db: Session = Depends(get_db)):
    return save_approval_record(db, payload.id, payload.model_dump(exclude={"id"}))


@app.put("/api/approvals/{record_id}", response_model=ApprovalRecordOut)
def update_approval(record_id: str, payload: ApprovalRecordIn, db: Session = Depends(get_db)):
    return save_approval_record(db, record_id, payload.model_dump(exclude={"id"}))


@app.get("/api/publishing-tasks", response_model=list[PublishingTaskOut])
def list_publishing_tasks(workspace_id: str = DEFAULT_WORKSPACE_ID, limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(PublishingTask).where(PublishingTask.workspace_id == workspace_id).order_by(PublishingTask.updated_at.desc()), limit, offset)


@app.post("/api/publishing-tasks", response_model=PublishingTaskOut)
def save_publishing_task(payload: PublishingTaskIn, db: Session = Depends(get_db)):
    return save_publishing_task_record(db, payload.id, payload.model_dump(exclude={"id"}))


@app.put("/api/publishing-tasks/{record_id}", response_model=PublishingTaskOut)
def update_publishing_task(record_id: str, payload: PublishingTaskIn, db: Session = Depends(get_db)):
    return save_publishing_task_record(db, record_id, payload.model_dump(exclude={"id"}))


@app.post("/api/publishing-tasks/{record_id}/tracking/start", response_model=AnalyticsRecordOut)
def start_publishing_tracking(record_id: str, workspace_id: str = DEFAULT_WORKSPACE_ID, db: Session = Depends(get_db)):
    return start_tracking(db, record_id, workspace_id)


@app.get("/api/tracking-snapshots", response_model=list[TrackingSnapshotOut])
def list_tracking_snapshots(workspace_id: str = DEFAULT_WORKSPACE_ID, limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(TrackingSnapshot).where(TrackingSnapshot.workspace_id == workspace_id).order_by(TrackingSnapshot.recorded_at.desc()), limit, offset)


@app.post("/api/tracking-snapshots", response_model=TrackingSnapshotOut)
def save_tracking_snapshot(payload: TrackingSnapshotIn, db: Session = Depends(get_db)):
    return append_tracking_snapshot(db, payload.id, payload.model_dump(exclude={"id"}))


@app.put("/api/tracking-snapshots/{record_id}", response_model=TrackingSnapshotOut)
def update_tracking_snapshot(record_id: str, payload: TrackingSnapshotIn, db: Session = Depends(get_db)):
    return append_tracking_snapshot(db, record_id, payload.model_dump(exclude={"id"}))


@app.get("/api/analytics-records", response_model=list[AnalyticsRecordOut])
def list_analytics_records(workspace_id: str = DEFAULT_WORKSPACE_ID, limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(AnalyticsRecord).where(AnalyticsRecord.workspace_id == workspace_id).order_by(AnalyticsRecord.updated_at.desc()), limit, offset)


@app.post("/api/analytics-records", response_model=AnalyticsRecordOut)
def save_analytics_record(payload: AnalyticsRecordIn, db: Session = Depends(get_db)):
    return save_analytics(db, payload.id, payload.model_dump(exclude={"id"}))


@app.put("/api/analytics-records/{record_id}", response_model=AnalyticsRecordOut)
def update_analytics_record(record_id: str, payload: AnalyticsRecordIn, db: Session = Depends(get_db)):
    return save_analytics(db, record_id, payload.model_dump(exclude={"id"}))


@app.get("/api/experience-records", response_model=list[ExperienceRecordOut])
def list_experience_records(workspace_id: str = DEFAULT_WORKSPACE_ID, limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(ExperienceRecord).where(ExperienceRecord.workspace_id == workspace_id).order_by(ExperienceRecord.updated_at.desc()), limit, offset)


@app.post("/api/experience-records", response_model=ExperienceRecordOut)
def save_experience_record(payload: ExperienceRecordIn, db: Session = Depends(get_db)):
    return save_experience(db, payload.id, payload.model_dump(exclude={"id"}))


@app.put("/api/experience-records/{record_id}", response_model=ExperienceRecordOut)
def update_experience_record(record_id: str, payload: ExperienceRecordIn, db: Session = Depends(get_db)):
    return save_experience(db, record_id, payload.model_dump(exclude={"id"}))


def topic_from_local(item: dict[str, Any]) -> TopicIn | None:
    if not item.get("id"):
        return None
    return TopicIn(
        id=item["id"],
        source=item.get("source") or item.get("sourcePlatform") or "mock",
        title=item.get("title") or "Untitled Topic",
        url=item.get("url") or item.get("canonicalUrl") or "",
        author=item.get("author") or "",
        category=item.get("category") or item.get("topic") or "",
        status=item.get("status") or "DISCOVERED",
        score=int(item.get("score") or item.get("finalScore") or 0),
        raw=item,
    )


def content_from_local(item: dict[str, Any]) -> ContentIn | None:
    if not item.get("id"):
        return None
    platforms = item.get("targetPlatforms") if isinstance(item.get("targetPlatforms"), list) else []
    return ContentIn(
        id=item["id"],
        topic_id=item.get("sourceTopicId") or item.get("primarySourceTopicId") or None,
        title=item.get("title") or "Untitled Content",
        status=item.get("status") or "DRAFT",
        platform=item.get("studioPlatform") or (platforms[0] if platforms else ""),
        content_type=item.get("studioFormat") or item.get("contentType") or "",
        source_url=item.get("sourceUrl") or "",
        raw=item,
    )


def knowledge_from_local(item: dict[str, Any]) -> KnowledgeEntryIn | None:
    if not item.get("id"):
        return None
    linked_content_ids = item.get("linkedContentIds") if isinstance(item.get("linkedContentIds"), list) else []
    source_url = item.get("sourceUrl") or ""
    knowledge_type = item.get("knowledgeType") or "Source / Research"
    if knowledge_type not in {"Fact", "Source / Research", "Inference", "Creator Preference", "Learning", "Playbook"}:
        knowledge_type = "Source / Research"
    status = item.get("status") or "ACTIVE"
    if status not in {"DRAFT", "ACTIVE", "ARCHIVED"}:
        status = "ACTIVE"
    return KnowledgeEntryIn(
        id=item["id"],
        topic_id=item.get("linkedTopicId") or item.get("primaryTopicId") or None,
        content_id=item.get("linkedContentId") or (linked_content_ids[0] if linked_content_ids else None),
        title=item.get("title") or "Untitled Knowledge",
        body=item.get("summary") or item.get("eventSummary") or "",
        knowledge_type=knowledge_type,
        source=item.get("source") or "",
        source_url=source_url,
        tags=item.get("tags") if isinstance(item.get("tags"), list) else [],
        confidence=max(0, min(100, int(item.get("confidence") or 70))),
        status=status,
        raw=item,
    )


def creator_profile_from_local(item: dict[str, Any] | None) -> CreatorProfileIn | None:
    if not item:
        return None
    return CreatorProfileIn(
        id="default",
        account_positioning=item.get("accountPositioning") or "",
        target_audience=item.get("targetAudience") or "",
        content_pillars=item.get("contentPillars") if isinstance(item.get("contentPillars"), list) else [],
        tone_style=item.get("toneStyle") or "",
        preferred_formats=item.get("preferredFormats") if isinstance(item.get("preferredFormats"), list) else [],
        topics_to_avoid=item.get("topicsToAvoid") if isinstance(item.get("topicsToAvoid"), list) else [],
        platform_preferences=item.get("platformPreferences") if isinstance(item.get("platformPreferences"), list) else [],
        raw=item,
    )


def opportunity_from_local(item: dict[str, Any]) -> ContentOpportunityIn | None:
    item_id = item.get("id")
    topic_id = item.get("topicId") or item.get("topic_id")
    if not item_id or not topic_id or not item.get("contentOpportunity"):
        return None
    return ContentOpportunityIn(
        id=item_id,
        workspace_id=item.get("workspaceId") or "default",
        topic_id=topic_id,
        creator_profile_id=item.get("creatorProfileId") or "default",
        developed_content_id=item.get("developedContentId") or None,
        analysis_batch_id=item.get("analysisBatchId") or f"import_{topic_id}",
        angle_key=item.get("angleKey") or "",
        knowledge_ids=item.get("knowledgeIds") if isinstance(item.get("knowledgeIds"), list) else [],
        summary=item.get("summary") or "",
        why_it_matters=item.get("whyItMatters") or "",
        audience=item.get("audience") or "",
        underlying_need_or_emotion=item.get("underlyingNeedOrEmotion") or "",
        content_opportunity=item.get("contentOpportunity") or "",
        recommended_format=item.get("recommendedFormat") or "",
        platform_fit=item.get("platformFit") if isinstance(item.get("platformFit"), list) else [],
        novelty=item.get("novelty") or 0,
        timeliness=item.get("timeliness") or 0,
        audience_fit=item.get("audienceFit") or 0,
        creator_fit=item.get("creatorFit") or 0,
        human_need_strength=item.get("humanNeedStrength") or 0,
        platform_fit_score=item.get("platformFitScore") or 0,
        visual_potential=item.get("visualPotential") or 0,
        production_difficulty=item.get("productionDifficulty") or 0,
        overall_score=item.get("overallScore") or 0,
        reasoning=item.get("reasoning") or "",
        status=str(item.get("status") or "candidate").casefold(),
        raw=item,
    )


def platform_version_id(content_id: str, platform: str, content_type: str, snapshot: dict[str, Any] | None = None) -> str:
    safe_platform = (platform or "unknown").replace(" ", "_")
    safe_type = (content_type or "draft").replace(" ", "_")
    suffix = f"_{stable_hash(snapshot)[:12]}" if snapshot else ""
    return f"pv_{content_id}_{safe_platform}_{safe_type}{suffix}"


def local_platform_snapshot(content: dict[str, Any], snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    source = snapshot or {}
    platform = source.get("platform") or content.get("studioPlatform") or (content.get("targetPlatforms") or ["小红书"])[0]
    content_type = source.get("contentType") or source.get("format") or content.get("studioFormat") or content.get("contentType") or "口播稿"
    return {
        "title": source.get("title") or content.get("draftTitle") or content.get("title") or "",
        "hook": source.get("hook") or content.get("draftHook") or content.get("recommendedHook") or "",
        "body": source.get("body") or content.get("draftBody") or content.get("body") or "",
        "tags": source.get("tags") if isinstance(source.get("tags"), list) else content.get("draftTags") if isinstance(content.get("draftTags"), list) else content.get("tags") if isinstance(content.get("tags"), list) else [],
        "platform": platform,
        "contentType": content_type,
        "sourceUrl": source.get("sourceUrl") or content.get("sourceUrl") or "",
    }


def platform_version_from_snapshot(
    content_id: str,
    snapshot: dict[str, Any],
    *,
    source: str,
    status: str = "DRAFT",
    immutable: bool = False,
) -> PlatformVersionIn:
    platform = snapshot.get("platform") or ""
    content_type = snapshot.get("contentType") or ""
    return PlatformVersionIn(
        id=platform_version_id(content_id, platform, content_type, snapshot),
        content_id=content_id,
        platform=platform,
        content_type=content_type,
        title=snapshot.get("title") or "",
        hook=snapshot.get("hook") or "",
        body=snapshot.get("body") or "",
        tags=snapshot.get("tags") if isinstance(snapshot.get("tags"), list) else [],
        status=canonical_status(status),
        is_immutable=immutable,
        raw={"source": source, "sourceUrl": snapshot.get("sourceUrl") or ""},
    )


def platform_versions_from_local(payload: LocalStorageBusinessImportIn) -> list[PlatformVersionIn]:
    versions: dict[str, PlatformVersionIn] = {}
    content_lookup = {item.get("id"): item for item in payload.contentItems if item.get("id")}
    for content in payload.contentItems:
        content_id = content.get("id")
        if not content_id:
            continue
        current_snapshot = local_platform_snapshot(content)
        current = platform_version_from_snapshot(content_id, current_snapshot, source="contentDraft", status=content.get("approvalStatus") or "DRAFT")
        versions[current.id] = current
        if content.get("approvalSnapshot"):
            approved_snapshot = local_platform_snapshot(content, content.get("approvalSnapshot"))
            approved = platform_version_from_snapshot(
                content_id,
                approved_snapshot,
                source="approvalSnapshot",
                status=content.get("approvalStatus") or "APPROVED",
                immutable=canonical_status(content.get("approvalStatus")) in {"APPROVED", "READY_TO_PUBLISH"},
            )
            versions[approved.id] = approved
    for job in payload.publishJobs:
        content_id = job.get("contentId")
        content = content_lookup.get(content_id)
        if not content_id or not content:
            continue
        job_snapshot = local_platform_snapshot(content, {
            "title": job.get("titleSnapshot"),
            "body": job.get("bodySnapshot"),
            "tags": job.get("tagsSnapshot"),
            "platform": job.get("platform"),
            "contentType": job.get("contentType"),
            "sourceUrl": content.get("sourceUrl"),
        })
        published = platform_version_from_snapshot(content_id, job_snapshot, source="publishingSnapshot", status="APPROVED", immutable=True)
        versions[published.id] = published
    for asset in payload.generatedAssets:
        content_id = asset.get("contentId")
        if not content_id:
            continue
        platform = asset.get("platform") or ""
        content_type = asset.get("assetType") or ""
        snapshot = {"title": asset.get("assetType") or "", "hook": "", "body": asset.get("content") or "", "tags": [], "platform": platform, "contentType": content_type, "sourceUrl": ""}
        version = platform_version_from_snapshot(content_id, snapshot, source="generatedAsset", status=asset.get("status") or "DRAFT")
        versions[version.id] = version
    return list(versions.values())


def approval_from_content(content: dict[str, Any]) -> ApprovalRecordIn | None:
    content_id = content.get("id")
    if not content_id:
        return None
    snapshot = local_platform_snapshot(content, content.get("approvalSnapshot") or None)
    version_id = platform_version_id(content_id, snapshot["platform"], snapshot["contentType"], snapshot)
    status = canonical_status(content.get("approvalStatus") or "DRAFT")
    return ApprovalRecordIn(
        id=f"approval_{content_id}_{version_id[-12:]}",
        content_id=content_id,
        platform_version_id=version_id,
        status=status,
        notes=content.get("approvalNotes") or "",
        reviewed_at=content.get("approvalReviewedAt") or None,
        approved_at=content.get("approvedAt") or None,
        invalidated_at=content.get("approvalInvalidatedAt") or None,
        invalidation_reason=content.get("approvalInvalidationReason") or "",
        snapshot=content.get("approvalSnapshot") or {},
        raw=content,
    )


def publishing_from_local(job: dict[str, Any], content_lookup: dict[str, dict[str, Any]]) -> PublishingTaskIn | None:
    job_id = job.get("id")
    content_id = job.get("contentId")
    if not job_id or not content_id:
        return None
    platform = job.get("platform") or ""
    content_type = job.get("contentType") or "口播稿"
    content = content_lookup.get(content_id) or {}
    snapshot = local_platform_snapshot(content, {
        "title": job.get("titleSnapshot"),
        "body": job.get("bodySnapshot"),
        "tags": job.get("tagsSnapshot"),
        "platform": platform,
        "contentType": content_type,
        "sourceUrl": content.get("sourceUrl"),
    })
    status = canonical_status(job.get("status") or "DRAFT")
    return PublishingTaskIn(
        id=job_id,
        content_id=content_id,
        platform_version_id=platform_version_id(content_id, platform, content_type, snapshot),
        platform=platform,
        content_type=content_type,
        scheduled_at=job.get("scheduledAt") or "",
        actual_published_at=job.get("actualPublishedAt") or (job.get("scheduledAt") if status == "PUBLISHED" and job.get("url") else ""),
        status=status,
        url=job.get("url") or "",
        notes=job.get("notes") or "",
        version_snapshot=snapshot,
        raw={**job, "migrationSource": "localStorage"},
    )


def analytics_from_local(record: dict[str, Any]) -> AnalyticsRecordIn | None:
    record_id = record.get("id")
    if not record_id:
        return None
    return AnalyticsRecordIn(
        id=record_id,
        publishing_task_id=record.get("publishJobId") or None,
        content_id=record.get("contentId") or None,
        platform=record.get("platform") or "",
        content_type=record.get("contentType") or "",
        stats_date=record.get("statsDate") or "",
        views=int(record.get("views") or 0),
        likes=int(record.get("likes") or 0),
        comments=int(record.get("comments") or 0),
        shares=int(record.get("shares") or 0),
        saves=int(record.get("saves") or 0),
        followers_gained=int(record.get("followersGained") or 0),
        tracking_status=canonical_status(record.get("trackingStatus") or "NOT_STARTED"),
        performance_analysis=record.get("performanceAnalysis") or record.get("aiPerformanceReview") or "",
        raw=record,
    )


def tracking_from_analytics(record: dict[str, Any]) -> list[TrackingSnapshotIn]:
    analytics_id = record.get("id")
    publish_job_id = record.get("publishJobId")
    snapshots = []
    if not analytics_id or not publish_job_id:
        return snapshots
    for checkpoint in record.get("checkpoints") or []:
        checkpoint_id = checkpoint.get("id") or "checkpoint"
        metrics = checkpoint.get("metrics") or {}
        status = canonical_status(checkpoint.get("status") or "PENDING")
        if status == "PENDING" and not metrics:
            continue
        snapshot_key = stable_hash({"checkpoint": checkpoint_id, "metrics": metrics, "updatedAt": checkpoint.get("updatedAt")})[:12]
        snapshots.append(TrackingSnapshotIn(
            id=f"track_{analytics_id}_{checkpoint_id}_{snapshot_key}",
            publishing_task_id=publish_job_id,
            analytics_record_id=analytics_id,
            checkpoint_id=checkpoint_id,
            label=checkpoint.get("label") or checkpoint_id,
            due_at=checkpoint.get("dueAt") or "",
            status=status,
            stats_date=metrics.get("statsDate") or record.get("statsDate") or "",
            metrics=metrics,
            recorded_at=checkpoint.get("updatedAt") or None,
            raw=checkpoint,
        ))
    return snapshots


def experience_from_local(item: dict[str, Any], publishing_lookup: dict[str, PublishingTaskIn]) -> ExperienceRecordIn | None:
    item_id = item.get("id")
    if not item_id:
        return None
    content_id = item.get("contentId") or None
    platform = item.get("platform") or ""
    content_type = item.get("contentType") or ""
    publishing = publishing_lookup.get(item.get("publishJobId"))
    return ExperienceRecordIn(
        id=item_id,
        content_id=content_id,
        topic_id=item.get("topicId") or None,
        platform_version_id=publishing.platform_version_id if publishing else None,
        publishing_task_id=item.get("publishJobId") or None,
        analytics_record_id=item.get("analyticsRecordId") or None,
        platform=platform,
        content_type=content_type,
        topic_category=item.get("topicCategory") or "",
        performance_result=item.get("performanceResult") or "",
        effective_practices=item.get("effectivePractices") if isinstance(item.get("effectivePractices"), list) else [],
        improvements=item.get("improvements") if isinstance(item.get("improvements"), list) else [],
        review_summary=item.get("reviewSummary") or "",
        reviewed_at=item.get("reviewedAt") or "",
        raw=item,
    )


def record_state(item: Any) -> str:
    if item is None:
        return ""
    values = {column.name: getattr(item, column.name) for column in item.__table__.columns if column.name not in {"created_at", "updated_at"}}
    return comparable_values(values)


def import_bucket(db: Session, items: list[dict[str, Any]], parser, model, entity_type: str, saver=None) -> ImportBucketSummary:
    summary = ImportBucketSummary()
    for raw_item in items:
        try:
            parsed = parser(raw_item)
            if not parsed:
                summary.failed += 1
                continue
            existing = db.get(model, parsed.id)
            before = record_state(existing)
            with db.begin_nested():
                if saver:
                    saved = saver(db, parsed.id, parsed.model_dump(exclude={"id"}), commit=False)
                else:
                    saved, _, _ = upsert(db, model, parsed.id, parsed.model_dump(exclude={"id"}), entity_type, commit=False)
            after = record_state(saved)
            if existing is None and saved.id == parsed.id:
                summary.added += 1
            elif before != after:
                summary.updated += 1
            else:
                summary.skipped += 1
        except Exception:
            summary.failed += 1
    return summary


def import_records(db: Session, records: list[Any], model, entity_type: str, saver=None) -> ImportBucketSummary:
    summary = ImportBucketSummary()
    for parsed in records:
        try:
            existing = db.get(model, parsed.id)
            before = record_state(existing)
            with db.begin_nested():
                if saver:
                    saved = saver(db, parsed.id, parsed.model_dump(exclude={"id"}), commit=False)
                else:
                    saved, _, _ = upsert(db, model, parsed.id, parsed.model_dump(exclude={"id"}), entity_type, commit=False)
            after = record_state(saved)
            if existing is None and saved.id == parsed.id:
                summary.added += 1
            elif before != after:
                summary.updated += 1
            else:
                summary.skipped += 1
        except Exception:
            summary.failed += 1
    return summary


@app.post("/api/import/localstorage-core", response_model=ImportSummary)
def import_localstorage_core(payload: LocalStorageCoreImportIn, db: Session = Depends(get_db)):
    ensure_workspace(db)
    creator_records = [record for record in [creator_profile_from_local(payload.creatorMemory)] if record]
    opportunity_records = [record for record in (opportunity_from_local(item) for item in payload.opportunityItems) if record]

    def save_imported_knowledge(session: Session, record_id: str, values: dict[str, Any], *, commit: bool = False):
        validate_knowledge_links(session, values)
        saved, _, _ = upsert(
            session,
            KnowledgeEntry,
            record_id,
            values,
            "KnowledgeEntry",
            create_action="knowledge_created",
            update_action="knowledge_updated",
            commit=commit,
        )
        assert_knowledge_type_boundary(saved)
        return saved

    summary = ImportSummary(
        topics=import_bucket(db, payload.topics, topic_from_local, Topic, "Topic"),
        contents=import_bucket(db, payload.contentItems, content_from_local, Content, "Content", save_content),
        knowledge=import_bucket(db, payload.knowledgeItems, knowledge_from_local, KnowledgeEntry, "KnowledgeEntry", save_imported_knowledge),
        creator_memory=import_records(db, creator_records, CreatorProfile, "CreatorProfile"),
        opportunities=import_records(db, opportunity_records, ContentOpportunity, "ContentOpportunity", import_opportunity_record),
    )
    log_activity(db, "import_localstorage_core", "Database", "localStorage", summary.model_dump(), workspace_id=DEFAULT_WORKSPACE_ID)
    db.commit()
    return summary


@app.post("/api/import/localstorage-business", response_model=BusinessImportSummary)
def import_localstorage_business(payload: LocalStorageBusinessImportIn, db: Session = Depends(get_db)):
    ensure_workspace(db)
    content_lookup = {item.get("id"): item for item in payload.contentItems if item.get("id")}
    platform_versions = platform_versions_from_local(payload)
    approvals = [record for record in (approval_from_content(item) for item in payload.contentItems) if record]
    publishing_tasks = [record for record in (publishing_from_local(item, content_lookup) for item in payload.publishJobs) if record]
    analytics_records = [record for record in (analytics_from_local(item) for item in payload.analyticsRecords) if record]
    tracking_snapshots = [snapshot for item in payload.analyticsRecords for snapshot in tracking_from_analytics(item)]
    publishing_lookup = {item.id: item for item in publishing_tasks}
    experience_records = [record for record in (experience_from_local(item, publishing_lookup) for item in payload.experienceItems) if record]

    version_id_map: dict[str, str] = {}

    def save_imported_version(session: Session, record_id: str, values: dict[str, Any], *, commit: bool = False):
        saved = save_platform_version_record(session, record_id, values, commit=commit)
        version_id_map[record_id] = saved.id
        return saved

    platform_summary = import_records(db, platform_versions, PlatformVersion, "PlatformVersion", save_imported_version)
    approvals = [record.model_copy(update={"platform_version_id": version_id_map.get(record.platform_version_id, record.platform_version_id)}) for record in approvals]
    publishing_tasks = [record.model_copy(update={"platform_version_id": version_id_map.get(record.platform_version_id, record.platform_version_id)}) for record in publishing_tasks]
    publishing_lookup = {item.id: item for item in publishing_tasks}
    experience_records = [record.model_copy(update={
        "platform_version_id": publishing_lookup.get(record.publishing_task_id).platform_version_id if publishing_lookup.get(record.publishing_task_id) else record.platform_version_id
    }) for record in experience_records]

    summary = BusinessImportSummary(
        platform_versions=platform_summary,
        approvals=import_records(db, approvals, ApprovalRecord, "ApprovalRecord", save_approval_record),
        publishing_tasks=import_records(db, publishing_tasks, PublishingTask, "PublishingTask", save_publishing_task_record),
        analytics_records=import_records(db, analytics_records, AnalyticsRecord, "AnalyticsRecord", save_analytics),
        tracking_snapshots=import_records(db, tracking_snapshots, TrackingSnapshot, "TrackingSnapshot", append_tracking_snapshot),
        experience_records=import_records(db, experience_records, ExperienceRecord, "ExperienceRecord", save_experience),
    )
    log_activity(db, "import_localstorage_business", "Database", "localStorage", summary.model_dump(), workspace_id=DEFAULT_WORKSPACE_ID)
    db.commit()
    return summary


@app.get("/api/knowledge/{knowledge_id}/export.md", response_class=PlainTextResponse)
def export_knowledge_markdown(knowledge_id: str, workspace_id: str = DEFAULT_WORKSPACE_ID, db: Session = Depends(get_db)):
    item = db.get(KnowledgeEntry, knowledge_id)
    if not item or item.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    log_activity(db, "export_markdown", "KnowledgeEntry", knowledge_id, {"format": "obsidian"}, workspace_id=workspace_id)
    db.commit()
    return PlainTextResponse(knowledge_to_markdown(item), media_type="text/markdown; charset=utf-8")


@app.post("/api/knowledge/export/markdown", response_model=MarkdownExportResponse)
def export_knowledge_batch_markdown(payload: MarkdownExportRequest, workspace_id: str = DEFAULT_WORKSPACE_ID, db: Session = Depends(get_db)):
    statement = select(KnowledgeEntry).where(KnowledgeEntry.workspace_id == workspace_id)
    if payload.ids:
        statement = statement.where(KnowledgeEntry.id.in_(payload.ids))
    items = list(db.scalars(statement.order_by(KnowledgeEntry.updated_at.desc())).all())
    files = [MarkdownFile(filename=safe_filename(item.title), content=knowledge_to_markdown(item)) for item in items]
    log_activity(db, "export_markdown", "KnowledgeEntry", "batch", {"count": len(files)}, workspace_id=workspace_id)
    db.commit()
    return MarkdownExportResponse(files=files)
