from typing import Any, TypeVar

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from .activity import log_activity
from .config import get_settings
from .database import get_db
from .models import ActivityLog, Content, KnowledgeEntry, Topic
from .obsidian import knowledge_to_markdown, safe_filename
from .schemas import (
    ActivityLogOut,
    ContentIn,
    ContentOut,
    ImportBucketSummary,
    ImportSummary,
    KnowledgeEntryIn,
    KnowledgeEntryOut,
    LocalStorageCoreImportIn,
    MarkdownExportRequest,
    MarkdownExportResponse,
    MarkdownFile,
    TopicIn,
    TopicOut,
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
    return {"status": "ok", "service": "ai-content-os-backend", "phase": "7A"}


@app.get("/health")
def health_alias() -> dict[str, str]:
    return api_health()


def list_records(db: Session, statement: Select, limit: int, offset: int) -> list[Any]:
    return list(db.scalars(statement.limit(limit).offset(offset)).all())


def upsert(db: Session, model: type[ModelT], record_id: str, values: dict[str, Any], entity_type: str) -> tuple[ModelT, bool]:
    existing = db.get(model, record_id)
    created = existing is None
    if existing:
        for key, value in values.items():
            setattr(existing, key, value)
        item = existing
    else:
        item = model(id=record_id, **values)
        db.add(item)
    log_activity(db, "create" if created else "update", entity_type, record_id, {"fields": sorted(values.keys())})
    db.commit()
    db.refresh(item)
    return item, created


@app.get("/api/topics", response_model=list[TopicOut])
def list_topics(limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(Topic).order_by(Topic.updated_at.desc()), limit, offset)


@app.post("/api/topics", response_model=TopicOut)
def create_topic(payload: TopicIn, db: Session = Depends(get_db)):
    item, _ = upsert(db, Topic, payload.id, payload.model_dump(exclude={"id"}), "Topic")
    return item


@app.put("/api/topics/{topic_id}", response_model=TopicOut)
def update_topic(topic_id: str, payload: TopicIn, db: Session = Depends(get_db)):
    values = payload.model_dump(exclude={"id"})
    item, _ = upsert(db, Topic, topic_id, values, "Topic")
    return item


@app.get("/api/contents", response_model=list[ContentOut])
def list_contents(limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(Content).order_by(Content.updated_at.desc()), limit, offset)


@app.post("/api/contents", response_model=ContentOut)
def create_content(payload: ContentIn, db: Session = Depends(get_db)):
    item, _ = upsert(db, Content, payload.id, payload.model_dump(exclude={"id"}), "Content")
    return item


@app.put("/api/contents/{content_id}", response_model=ContentOut)
def update_content(content_id: str, payload: ContentIn, db: Session = Depends(get_db)):
    item, _ = upsert(db, Content, content_id, payload.model_dump(exclude={"id"}), "Content")
    return item


@app.get("/api/knowledge", response_model=list[KnowledgeEntryOut])
def list_knowledge(limit: int = Query(100, le=500), offset: int = 0, db: Session = Depends(get_db)):
    return list_records(db, select(KnowledgeEntry).order_by(KnowledgeEntry.updated_at.desc()), limit, offset)


@app.post("/api/knowledge", response_model=KnowledgeEntryOut)
def create_knowledge(payload: KnowledgeEntryIn, db: Session = Depends(get_db)):
    item, _ = upsert(db, KnowledgeEntry, payload.id, payload.model_dump(exclude={"id"}), "KnowledgeEntry")
    return item


@app.put("/api/knowledge/{knowledge_id}", response_model=KnowledgeEntryOut)
def update_knowledge(knowledge_id: str, payload: KnowledgeEntryIn, db: Session = Depends(get_db)):
    item, _ = upsert(db, KnowledgeEntry, knowledge_id, payload.model_dump(exclude={"id"}), "KnowledgeEntry")
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


def import_bucket(db: Session, items: list[dict[str, Any]], parser, model, entity_type: str) -> ImportBucketSummary:
    summary = ImportBucketSummary()
    for raw_item in items:
        try:
            parsed = parser(raw_item)
            if not parsed:
                summary.failed += 1
                continue
            exists = db.get(model, parsed.id) is not None
            upsert(db, model, parsed.id, parsed.model_dump(exclude={"id"}), entity_type)
            if exists:
                summary.skipped += 1
            else:
                summary.added += 1
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
