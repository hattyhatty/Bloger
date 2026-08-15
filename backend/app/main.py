import json
from datetime import datetime, timezone
from typing import Any, TypeVar

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from .activity import log_activity
from .config import get_settings
from .database import get_db
from .models import (
    ActivityLog,
    AnalyticsRecord,
    ApprovalRecord,
    Content,
    ExperienceRecord,
    KnowledgeEntry,
    PlatformVersion,
    PublishingTask,
    Topic,
    TrackingSnapshot,
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
    PlatformVersionIn,
    PlatformVersionOut,
    PublishingTaskIn,
    PublishingTaskOut,
    TopicIn,
    TopicOut,
    TrackingSnapshotIn,
    TrackingSnapshotOut,
)


settings = get_settings()
app = FastAPI(title="AI Content OS Backend", version="0.7.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ModelT = TypeVar("ModelT")


@app.get("/api/health")
def api_health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-content-os-backend", "phase": "7B"}


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


def upsert(db: Session, model: type[ModelT], record_id: str, values: dict[str, Any], entity_type: str) -> tuple[ModelT, bool, bool]:
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
        log_activity(db, "create" if created else "update", entity_type, record_id, {"fields": sorted(values.keys())})
    db.commit()
    db.refresh(item)
    return item, created, changed


@app.get("/api/topics", response_model=list[TopicOut])
def list_topics(limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(Topic).order_by(Topic.updated_at.desc()), limit, offset)


@app.post("/api/topics", response_model=TopicOut)
def create_topic(payload: TopicIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, Topic, payload.id, payload.model_dump(exclude={"id"}), "Topic")
    return item


@app.put("/api/topics/{topic_id}", response_model=TopicOut)
def update_topic(topic_id: str, payload: TopicIn, db: Session = Depends(get_db)):
    values = payload.model_dump(exclude={"id"})
    item, _, _ = upsert(db, Topic, topic_id, values, "Topic")
    return item


@app.get("/api/contents", response_model=list[ContentOut])
def list_contents(limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(Content).order_by(Content.updated_at.desc()), limit, offset)


@app.post("/api/contents", response_model=ContentOut)
def create_content(payload: ContentIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, Content, payload.id, payload.model_dump(exclude={"id"}), "Content")
    return item


@app.put("/api/contents/{content_id}", response_model=ContentOut)
def update_content(content_id: str, payload: ContentIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, Content, content_id, payload.model_dump(exclude={"id"}), "Content")
    return item


@app.get("/api/knowledge", response_model=list[KnowledgeEntryOut])
def list_knowledge(limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(KnowledgeEntry).order_by(KnowledgeEntry.updated_at.desc()), limit, offset)


@app.post("/api/knowledge", response_model=KnowledgeEntryOut)
def create_knowledge(payload: KnowledgeEntryIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, KnowledgeEntry, payload.id, payload.model_dump(exclude={"id"}), "KnowledgeEntry")
    return item


@app.put("/api/knowledge/{knowledge_id}", response_model=KnowledgeEntryOut)
def update_knowledge(knowledge_id: str, payload: KnowledgeEntryIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, KnowledgeEntry, knowledge_id, payload.model_dump(exclude={"id"}), "KnowledgeEntry")
    return item


@app.delete("/api/knowledge/{knowledge_id}")
def delete_knowledge(knowledge_id: str, db: Session = Depends(get_db)):
    item = db.get(KnowledgeEntry, knowledge_id)
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    db.delete(item)
    log_activity(db, "delete", "KnowledgeEntry", knowledge_id, {})
    db.commit()
    return {"ok": True}


@app.get("/api/activity-logs", response_model=list[ActivityLogOut])
def list_activity_logs(limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(ActivityLog).order_by(ActivityLog.created_at.desc()), limit, offset)


@app.get("/api/platform-versions", response_model=list[PlatformVersionOut])
def list_platform_versions(limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(PlatformVersion).order_by(PlatformVersion.updated_at.desc()), limit, offset)


@app.post("/api/platform-versions", response_model=PlatformVersionOut)
def save_platform_version(payload: PlatformVersionIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, PlatformVersion, payload.id, payload.model_dump(exclude={"id"}), "PlatformVersion")
    return item


@app.put("/api/platform-versions/{record_id}", response_model=PlatformVersionOut)
def update_platform_version(record_id: str, payload: PlatformVersionIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, PlatformVersion, record_id, payload.model_dump(exclude={"id"}), "PlatformVersion")
    return item


@app.get("/api/approvals", response_model=list[ApprovalRecordOut])
def list_approvals(limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(ApprovalRecord).order_by(ApprovalRecord.updated_at.desc()), limit, offset)


@app.post("/api/approvals", response_model=ApprovalRecordOut)
def save_approval(payload: ApprovalRecordIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, ApprovalRecord, payload.id, payload.model_dump(exclude={"id"}), "ApprovalRecord")
    return item


@app.put("/api/approvals/{record_id}", response_model=ApprovalRecordOut)
def update_approval(record_id: str, payload: ApprovalRecordIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, ApprovalRecord, record_id, payload.model_dump(exclude={"id"}), "ApprovalRecord")
    return item


@app.get("/api/publishing-tasks", response_model=list[PublishingTaskOut])
def list_publishing_tasks(limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(PublishingTask).order_by(PublishingTask.updated_at.desc()), limit, offset)


@app.post("/api/publishing-tasks", response_model=PublishingTaskOut)
def save_publishing_task(payload: PublishingTaskIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, PublishingTask, payload.id, payload.model_dump(exclude={"id"}), "PublishingTask")
    return item


@app.put("/api/publishing-tasks/{record_id}", response_model=PublishingTaskOut)
def update_publishing_task(record_id: str, payload: PublishingTaskIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, PublishingTask, record_id, payload.model_dump(exclude={"id"}), "PublishingTask")
    return item


@app.get("/api/tracking-snapshots", response_model=list[TrackingSnapshotOut])
def list_tracking_snapshots(limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(TrackingSnapshot).order_by(TrackingSnapshot.updated_at.desc()), limit, offset)


@app.post("/api/tracking-snapshots", response_model=TrackingSnapshotOut)
def save_tracking_snapshot(payload: TrackingSnapshotIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, TrackingSnapshot, payload.id, payload.model_dump(exclude={"id"}), "TrackingSnapshot")
    return item


@app.put("/api/tracking-snapshots/{record_id}", response_model=TrackingSnapshotOut)
def update_tracking_snapshot(record_id: str, payload: TrackingSnapshotIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, TrackingSnapshot, record_id, payload.model_dump(exclude={"id"}), "TrackingSnapshot")
    return item


@app.get("/api/analytics-records", response_model=list[AnalyticsRecordOut])
def list_analytics_records(limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(AnalyticsRecord).order_by(AnalyticsRecord.updated_at.desc()), limit, offset)


@app.post("/api/analytics-records", response_model=AnalyticsRecordOut)
def save_analytics_record(payload: AnalyticsRecordIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, AnalyticsRecord, payload.id, payload.model_dump(exclude={"id"}), "AnalyticsRecord")
    return item


@app.put("/api/analytics-records/{record_id}", response_model=AnalyticsRecordOut)
def update_analytics_record(record_id: str, payload: AnalyticsRecordIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, AnalyticsRecord, record_id, payload.model_dump(exclude={"id"}), "AnalyticsRecord")
    return item


@app.get("/api/experience-records", response_model=list[ExperienceRecordOut])
def list_experience_records(limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(ExperienceRecord).order_by(ExperienceRecord.updated_at.desc()), limit, offset)


@app.post("/api/experience-records", response_model=ExperienceRecordOut)
def save_experience_record(payload: ExperienceRecordIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, ExperienceRecord, payload.id, payload.model_dump(exclude={"id"}), "ExperienceRecord")
    return item


@app.put("/api/experience-records/{record_id}", response_model=ExperienceRecordOut)
def update_experience_record(record_id: str, payload: ExperienceRecordIn, db: Session = Depends(get_db)):
    item, _, _ = upsert(db, ExperienceRecord, record_id, payload.model_dump(exclude={"id"}), "ExperienceRecord")
    return item


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
    source_url = item.get("sourceUrl") or item.get("source") or ""
    return KnowledgeEntryIn(
        id=item["id"],
        topic_id=item.get("linkedTopicId") or item.get("primaryTopicId") or None,
        content_id=linked_content_ids[0] if linked_content_ids else None,
        title=item.get("title") or "Untitled Knowledge",
        body=item.get("summary") or item.get("eventSummary") or "",
        source_url=source_url,
        tags=item.get("tags") if isinstance(item.get("tags"), list) else [],
        raw=item,
    )


def platform_version_id(content_id: str, platform: str, content_type: str) -> str:
    safe_platform = (platform or "unknown").replace(" ", "_")
    safe_type = (content_type or "draft").replace(" ", "_")
    return f"pv_{content_id}_{safe_platform}_{safe_type}"


def platform_versions_from_local(payload: LocalStorageBusinessImportIn) -> list[PlatformVersionIn]:
    versions: dict[str, PlatformVersionIn] = {}
    for content in payload.contentItems:
        content_id = content.get("id")
        if not content_id:
            continue
        platform = content.get("studioPlatform") or (content.get("targetPlatforms") or ["小红书"])[0]
        content_type = content.get("studioFormat") or content.get("contentType") or "口播稿"
        record_id = platform_version_id(content_id, platform, content_type)
        versions[record_id] = PlatformVersionIn(
            id=record_id,
            content_id=content_id,
            platform=platform,
            content_type=content_type,
            title=content.get("draftTitle") or content.get("title") or "",
            hook=content.get("draftHook") or content.get("recommendedHook") or "",
            body=content.get("draftBody") or content.get("body") or "",
            tags=content.get("draftTags") if isinstance(content.get("draftTags"), list) else content.get("tags") if isinstance(content.get("tags"), list) else [],
            status=content.get("approvalStatus") or "DRAFT",
            raw={"source": "contentDraft", **content},
        )
    for asset in payload.generatedAssets:
        content_id = asset.get("contentId")
        if not content_id:
            continue
        platform = asset.get("platform") or ""
        content_type = asset.get("assetType") or ""
        record_id = f"pv_asset_{asset.get('id')}"
        versions[record_id] = PlatformVersionIn(
            id=record_id,
            content_id=content_id,
            platform=platform,
            content_type=content_type,
            title=asset.get("assetType") or "",
            body=asset.get("content") or "",
            status=asset.get("status") or "DRAFT",
            raw={"source": "generatedAsset", **asset},
        )
    return list(versions.values())


def approval_from_content(content: dict[str, Any]) -> ApprovalRecordIn | None:
    content_id = content.get("id")
    if not content_id:
        return None
    return ApprovalRecordIn(
        id=f"approval_{content_id}",
        content_id=content_id,
        status=content.get("approvalStatus") or "DRAFT",
        notes=content.get("approvalNotes") or "",
        reviewed_at=content.get("approvalReviewedAt") or None,
        approved_at=content.get("approvedAt") or None,
        invalidated_at=content.get("approvalInvalidatedAt") or None,
        invalidation_reason=content.get("approvalInvalidationReason") or "",
        snapshot=content.get("approvalSnapshot") or {},
        raw=content,
    )


def publishing_from_local(job: dict[str, Any]) -> PublishingTaskIn | None:
    job_id = job.get("id")
    content_id = job.get("contentId")
    if not job_id or not content_id:
        return None
    platform = job.get("platform") or ""
    content_type = job.get("contentType") or "口播稿"
    return PublishingTaskIn(
        id=job_id,
        content_id=content_id,
        platform_version_id=platform_version_id(content_id, platform, content_type),
        platform=platform,
        content_type=content_type,
        scheduled_at=job.get("scheduledAt") or "",
        actual_published_at=job.get("actualPublishedAt") or "",
        status=job.get("status") or "DRAFT",
        url=job.get("url") or "",
        notes=job.get("notes") or "",
        raw=job,
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
        tracking_status=record.get("trackingStatus") or "NOT_STARTED",
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
        snapshots.append(TrackingSnapshotIn(
            id=f"track_{analytics_id}_{checkpoint_id}",
            publishing_task_id=publish_job_id,
            analytics_record_id=analytics_id,
            checkpoint_id=checkpoint_id,
            label=checkpoint.get("label") or checkpoint_id,
            due_at=checkpoint.get("dueAt") or "",
            status=checkpoint.get("status") or "PENDING",
            stats_date=metrics.get("statsDate") or record.get("statsDate") or "",
            metrics=metrics,
            raw=checkpoint,
        ))
    return snapshots


def experience_from_local(item: dict[str, Any]) -> ExperienceRecordIn | None:
    item_id = item.get("id")
    if not item_id:
        return None
    content_id = item.get("contentId") or None
    platform = item.get("platform") or ""
    content_type = item.get("contentType") or ""
    return ExperienceRecordIn(
        id=item_id,
        content_id=content_id,
        topic_id=item.get("topicId") or None,
        platform_version_id=platform_version_id(content_id, platform, content_type) if content_id else None,
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


def import_bucket(db: Session, items: list[dict[str, Any]], parser, model, entity_type: str) -> ImportBucketSummary:
    summary = ImportBucketSummary()
    for raw_item in items:
        try:
            parsed = parser(raw_item)
            if not parsed:
                summary.failed += 1
                continue
            exists = db.get(model, parsed.id) is not None
            _, created, changed = upsert(db, model, parsed.id, parsed.model_dump(exclude={"id"}), entity_type)
            if created:
                summary.added += 1
            elif changed:
                summary.updated += 1
            elif exists:
                summary.skipped += 1
            else:
                summary.failed += 1
        except Exception:
            db.rollback()
            summary.failed += 1
    return summary


def import_records(db: Session, records: list[Any], model, entity_type: str) -> ImportBucketSummary:
    summary = ImportBucketSummary()
    for parsed in records:
        try:
            exists = db.get(model, parsed.id) is not None
            _, created, changed = upsert(db, model, parsed.id, parsed.model_dump(exclude={"id"}), entity_type)
            if created:
                summary.added += 1
            elif changed:
                summary.updated += 1
            elif exists:
                summary.skipped += 1
            else:
                summary.failed += 1
        except Exception:
            db.rollback()
            summary.failed += 1
    return summary


@app.post("/api/import/localstorage-core", response_model=ImportSummary)
def import_localstorage_core(payload: LocalStorageCoreImportIn, db: Session = Depends(get_db)):
    summary = ImportSummary(
        topics=import_bucket(db, payload.topics, topic_from_local, Topic, "Topic"),
        contents=import_bucket(db, payload.contentItems, content_from_local, Content, "Content"),
        knowledge=import_bucket(db, payload.knowledgeItems, knowledge_from_local, KnowledgeEntry, "KnowledgeEntry"),
    )
    log_activity(db, "import_localstorage_core", "Database", "localStorage", summary.model_dump())
    db.commit()
    return summary


@app.post("/api/import/localstorage-business", response_model=BusinessImportSummary)
def import_localstorage_business(payload: LocalStorageBusinessImportIn, db: Session = Depends(get_db)):
    platform_versions = platform_versions_from_local(payload)
    approvals = [record for record in (approval_from_content(item) for item in payload.contentItems) if record]
    publishing_tasks = [record for record in (publishing_from_local(item) for item in payload.publishJobs) if record]
    analytics_records = [record for record in (analytics_from_local(item) for item in payload.analyticsRecords) if record]
    tracking_snapshots = [snapshot for item in payload.analyticsRecords for snapshot in tracking_from_analytics(item)]
    experience_records = [record for record in (experience_from_local(item) for item in payload.experienceItems) if record]

    summary = BusinessImportSummary(
        platform_versions=import_records(db, platform_versions, PlatformVersion, "PlatformVersion"),
        approvals=import_records(db, approvals, ApprovalRecord, "ApprovalRecord"),
        publishing_tasks=import_records(db, publishing_tasks, PublishingTask, "PublishingTask"),
        analytics_records=import_records(db, analytics_records, AnalyticsRecord, "AnalyticsRecord"),
        tracking_snapshots=import_records(db, tracking_snapshots, TrackingSnapshot, "TrackingSnapshot"),
        experience_records=import_records(db, experience_records, ExperienceRecord, "ExperienceRecord"),
    )
    log_activity(db, "import_localstorage_business", "Database", "localStorage", summary.model_dump())
    db.commit()
    return summary


@app.get("/api/knowledge/{knowledge_id}/export.md", response_class=PlainTextResponse)
def export_knowledge_markdown(knowledge_id: str, db: Session = Depends(get_db)):
    item = db.get(KnowledgeEntry, knowledge_id)
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    log_activity(db, "export_markdown", "KnowledgeEntry", knowledge_id, {"format": "obsidian"})
    db.commit()
    return PlainTextResponse(knowledge_to_markdown(item), media_type="text/markdown; charset=utf-8")


@app.post("/api/knowledge/export/markdown", response_model=MarkdownExportResponse)
def export_knowledge_batch_markdown(payload: MarkdownExportRequest, db: Session = Depends(get_db)):
    statement = select(KnowledgeEntry)
    if payload.ids:
        statement = statement.where(KnowledgeEntry.id.in_(payload.ids))
    items = list(db.scalars(statement.order_by(KnowledgeEntry.updated_at.desc())).all())
    files = [MarkdownFile(filename=safe_filename(item.title), content=knowledge_to_markdown(item)) for item in items]
    log_activity(db, "export_markdown", "KnowledgeEntry", "batch", {"count": len(files)})
    db.commit()
    return MarkdownExportResponse(files=files)
