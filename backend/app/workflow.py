"""Central business invariants for the single-workspace content workflow.

UI code may be optimistic while offline, but every authoritative write passes through
this module when the backend is available. Provider/model code deliberately does not
belong here.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .activity import log_activity
from .models import (
    AnalyticsRecord,
    ApprovalRecord,
    Content,
    ExperienceRecord,
    KnowledgeEntry,
    PlatformVersion,
    PublishingTask,
    Topic,
    TrackingSnapshot,
    Workspace,
)


DEFAULT_WORKSPACE_ID = "default"
APPROVED_STATUSES = {"APPROVED", "READY_TO_PUBLISH"}
WORKFLOW_MANAGED_CONTENT_STATUSES = {
    "IN_REVIEW",
    "CHANGES_REQUESTED",
    "APPROVED",
    "READY_TO_PUBLISH",
    "SCHEDULED",
    "PUBLISHED",
    "TRACKING",
}
PUBLISH_STATUSES = {"DRAFT", "READY", "SCHEDULED", "PUBLISHED", "FAILED", "CANCELLED"}
PUBLISH_TRANSITIONS = {
    "DRAFT": {"DRAFT", "READY", "SCHEDULED", "CANCELLED"},
    "READY": {"READY", "SCHEDULED", "PUBLISHED", "FAILED", "CANCELLED"},
    "SCHEDULED": {"SCHEDULED", "READY", "PUBLISHED", "FAILED", "CANCELLED"},
    "FAILED": {"FAILED", "READY", "SCHEDULED", "CANCELLED"},
    "PUBLISHED": {"PUBLISHED"},
    "CANCELLED": {"CANCELLED"},
}


class WorkflowConflict(ValueError):
    """Raised when a request violates an authoritative workflow invariant."""


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def canonical_status(value: str | None, default: str = "DRAFT") -> str:
    text = str(value or default).strip().replace("-", "_").replace(" ", "_").upper()
    aliases = {
        "INREVIEW": "IN_REVIEW",
        "CHANGESREQUESTED": "CHANGES_REQUESTED",
        "READYTOPUBLISH": "READY_TO_PUBLISH",
        "NOTSTARTED": "NOT_STARTED",
    }
    return aliases.get(text.replace("_", ""), text)


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def ensure_workspace(db: Session, workspace_id: str = DEFAULT_WORKSPACE_ID) -> Workspace:
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        workspace = Workspace(id=workspace_id, name="Default Workspace" if workspace_id == DEFAULT_WORKSPACE_ID else workspace_id)
        db.add(workspace)
        db.flush()
    return workspace


def ensure_owned(entity: Any, workspace_id: str, label: str) -> None:
    if entity is None:
        raise WorkflowConflict(f"{label} not found")
    if getattr(entity, "workspace_id", workspace_id) != workspace_id:
        raise WorkflowConflict(f"{label} belongs to another workspace")


def content_snapshot(values: dict[str, Any]) -> dict[str, Any]:
    raw = values.get("raw") or {}
    return {
        "title": raw.get("draftTitle") or values.get("title") or "",
        "hook": raw.get("draftHook") or "",
        "body": raw.get("draftBody") or raw.get("body") or "",
        "tags": raw.get("draftTags") or raw.get("tags") or [],
        "platform": raw.get("studioPlatform") or values.get("platform") or "",
        "contentType": raw.get("studioFormat") or values.get("content_type") or "",
        "sourceUrl": raw.get("sourceUrl") or values.get("source_url") or "",
    }


def platform_snapshot(version: PlatformVersion) -> dict[str, Any]:
    source_url = (version.raw or {}).get("sourceUrl") or (version.raw or {}).get("source_url") or ""
    return {
        "platformVersionId": version.id,
        "revision": version.revision,
        "contentHash": version.content_hash,
        "title": version.title,
        "hook": version.hook,
        "body": version.body,
        "tags": list(version.tags or []),
        "platform": version.platform,
        "contentType": version.content_type,
        "sourceUrl": source_url,
    }


def platform_values_hash(values: dict[str, Any]) -> str:
    return stable_hash({
        "title": values.get("title") or "",
        "hook": values.get("hook") or "",
        "body": values.get("body") or "",
        "tags": values.get("tags") or [],
        "platform": values.get("platform") or "",
        "contentType": values.get("content_type") or "",
        "sourceUrl": (values.get("raw") or {}).get("sourceUrl") or "",
    })


def _finish(db: Session, item: Any, commit: bool) -> Any:
    db.flush()
    if commit:
        db.commit()
        db.refresh(item)
    return item


def save_content(db: Session, record_id: str, values: dict[str, Any], *, commit: bool = True) -> Content:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    ensure_workspace(db, workspace_id)
    topic_id = values.get("topic_id")
    if topic_id:
        ensure_owned(db.get(Topic, topic_id), workspace_id, "Topic")

    existing = db.get(Content, record_id)
    new_hash = stable_hash(content_snapshot(values))
    if existing is None:
        create_values = {**values, "workspace_id": workspace_id, "revision": 1, "content_hash": new_hash}
        if canonical_status(create_values.get("status")) in WORKFLOW_MANAGED_CONTENT_STATUSES:
            create_values["status"] = "DRAFT"
        item = Content(id=record_id, **create_values)
        db.add(item)
        log_activity(db, "create", "Content", record_id, {"revision": 1}, workspace_id=workspace_id)
        return _finish(db, item, commit)

    ensure_owned(existing, workspace_id, "Content")
    has_current_hash = len(existing.content_hash or "") == 64
    changed_version = bool(has_current_hash and existing.content_hash != new_hash)
    for key, value in values.items():
        if key not in {"revision", "content_hash"}:
            if key == "status" and (
                canonical_status(value) in WORKFLOW_MANAGED_CONTENT_STATUSES
                or canonical_status(existing.status) in WORKFLOW_MANAGED_CONTENT_STATUSES
            ):
                continue
            setattr(existing, key, value)
    if changed_version:
        existing.revision += 1
        existing.content_hash = new_hash
        invalidated = list(db.scalars(select(ApprovalRecord).where(
            ApprovalRecord.content_id == record_id,
            ApprovalRecord.workspace_id == workspace_id,
        )).all())
        for approval in invalidated:
            if canonical_status(approval.status) in APPROVED_STATUSES:
                approval.status = "DRAFT"
                approval.invalidated_at = utcnow()
                approval.invalidation_reason = "Content changed after approval"
                log_activity(
                    db,
                    "approval_invalidated",
                    "ApprovalRecord",
                    approval.id,
                    {"contentId": record_id, "revision": existing.revision},
                    workspace_id=workspace_id,
                )
        if canonical_status(existing.status) in APPROVED_STATUSES:
            existing.status = "DRAFT"
    elif not has_current_hash:
        existing.content_hash = new_hash
    log_activity(
        db,
        "content_revision_created" if changed_version else "update",
        "Content",
        record_id,
        {"revision": existing.revision, "versionChanged": changed_version},
        workspace_id=workspace_id,
    )
    return _finish(db, existing, commit)


def save_platform_version(db: Session, record_id: str, values: dict[str, Any], *, commit: bool = True) -> PlatformVersion:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    ensure_workspace(db, workspace_id)
    content = db.get(Content, values.get("content_id"))
    ensure_owned(content, workspace_id, "Content")
    expected_hash = platform_values_hash(values)
    existing = db.get(PlatformVersion, record_id)
    if existing:
        ensure_owned(existing, workspace_id, "PlatformVersion")
        if existing.content_id != content.id:
            raise WorkflowConflict("PlatformVersion Content binding is immutable")
        has_current_hash = len(existing.content_hash or "") == 64
        if existing.is_immutable and has_current_hash and existing.content_hash != expected_hash:
            raise WorkflowConflict("Approved or published platform versions are immutable")
        for key, value in values.items():
            if key not in {"revision", "content_hash", "is_immutable"}:
                setattr(existing, key, value)
        existing.content_hash = expected_hash
        existing.is_immutable = existing.is_immutable or bool(values.get("is_immutable"))
        if not has_current_hash:
            for approval in db.scalars(select(ApprovalRecord).where(ApprovalRecord.platform_version_id == existing.id)).all():
                approval.snapshot_hash = expected_hash
                approval.snapshot = {**(approval.snapshot or {}), "contentHash": expected_hash}
            for job in db.scalars(select(PublishingTask).where(PublishingTask.platform_version_id == existing.id)).all():
                job.version_snapshot = {**(job.version_snapshot or {}), "contentHash": expected_hash}
        log_activity(db, "update", "PlatformVersion", record_id, {"revision": existing.revision}, workspace_id=workspace_id)
        return _finish(db, existing, commit)

    same = db.scalar(select(PlatformVersion).where(
        PlatformVersion.workspace_id == workspace_id,
        PlatformVersion.content_id == content.id,
        PlatformVersion.platform == (values.get("platform") or ""),
        PlatformVersion.content_type == (values.get("content_type") or ""),
        PlatformVersion.content_hash == expected_hash,
    ))
    if same:
        return same
    latest_revision = db.scalar(select(func.max(PlatformVersion.revision)).where(
        PlatformVersion.content_id == content.id,
        PlatformVersion.platform == (values.get("platform") or ""),
        PlatformVersion.content_type == (values.get("content_type") or ""),
    )) or 0
    item_values = {
        **values,
        "workspace_id": workspace_id,
        "revision": latest_revision + 1,
        "content_hash": expected_hash,
        "is_immutable": bool(values.get("is_immutable")),
    }
    item = PlatformVersion(id=record_id, **item_values)
    db.add(item)
    log_activity(db, "platform_version_created", "PlatformVersion", record_id, {"revision": item.revision}, workspace_id=workspace_id)
    return _finish(db, item, commit)


def active_approval(db: Session, content_id: str, platform_version_id: str, workspace_id: str) -> ApprovalRecord | None:
    approvals = db.scalars(select(ApprovalRecord).where(
        ApprovalRecord.workspace_id == workspace_id,
        ApprovalRecord.content_id == content_id,
        ApprovalRecord.platform_version_id == platform_version_id,
    ).order_by(ApprovalRecord.approved_at.desc().nullslast(), ApprovalRecord.updated_at.desc())).all()
    return next((item for item in approvals if canonical_status(item.status) in APPROVED_STATUSES and not item.invalidated_at), None)


def save_approval(db: Session, record_id: str, values: dict[str, Any], *, commit: bool = True) -> ApprovalRecord:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    ensure_workspace(db, workspace_id)
    content = db.get(Content, values.get("content_id"))
    ensure_owned(content, workspace_id, "Content")
    status = canonical_status(values.get("status"))
    version = db.get(PlatformVersion, values.get("platform_version_id")) if values.get("platform_version_id") else None
    if status in APPROVED_STATUSES:
        ensure_owned(version, workspace_id, "PlatformVersion")
        if version.content_id != content.id:
            raise WorkflowConflict("Approval platform version does not belong to Content")
        same = active_approval(db, content.id, version.id, workspace_id)
        if same and same.id != record_id:
            return same
        for prior in db.scalars(select(ApprovalRecord).where(
            ApprovalRecord.workspace_id == workspace_id,
            ApprovalRecord.content_id == content.id,
        )).all():
            if prior.id != record_id and canonical_status(prior.status) in APPROVED_STATUSES:
                prior.status = "DRAFT"
                prior.invalidated_at = utcnow()
                prior.invalidation_reason = "Superseded by a newer approved version"
                log_activity(db, "approval_invalidated", "ApprovalRecord", prior.id, {"supersededBy": record_id}, workspace_id=workspace_id)
        version.is_immutable = True
        values = {
            **values,
            "platform_version_revision": version.revision,
            "snapshot": platform_snapshot(version),
            "snapshot_hash": version.content_hash,
            "approved_at": values.get("approved_at") or utcnow(),
            "invalidated_at": None,
            "invalidation_reason": "",
        }
        content.status = "APPROVED" if status == "APPROVED" else "READY_TO_PUBLISH"
    values = {**values, "workspace_id": workspace_id, "status": status}
    existing = db.get(ApprovalRecord, record_id)
    if existing:
        ensure_owned(existing, workspace_id, "ApprovalRecord")
        for key, value in values.items():
            setattr(existing, key, value)
        item = existing
    else:
        item = ApprovalRecord(id=record_id, **values)
        db.add(item)
    if status == "DRAFT" and canonical_status(content.status) in APPROVED_STATUSES:
        content.status = "DRAFT"
    elif status == "IN_REVIEW":
        content.status = "IN_REVIEW"
    elif status == "CHANGES_REQUESTED":
        content.status = "CHANGES_REQUESTED"
    action = "content_approved" if status in APPROVED_STATUSES else "approval_revoked" if status == "DRAFT" else "approval_status_changed"
    log_activity(db, action, "ApprovalRecord", record_id, {"contentId": content.id, "platformVersionId": values.get("platform_version_id"), "status": status}, workspace_id=workspace_id)
    return _finish(db, item, commit)


def _validated_publish_status(value: str | None) -> str:
    status = canonical_status(value)
    if status not in PUBLISH_STATUSES:
        raise WorkflowConflict(f"Unsupported publishing status: {status}")
    return status


def save_publishing_task(db: Session, record_id: str, values: dict[str, Any], *, commit: bool = True) -> PublishingTask:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    ensure_workspace(db, workspace_id)
    content = db.get(Content, values.get("content_id"))
    version = db.get(PlatformVersion, values.get("platform_version_id")) if values.get("platform_version_id") else None
    ensure_owned(content, workspace_id, "Content")
    ensure_owned(version, workspace_id, "PlatformVersion")
    if version.content_id != content.id:
        raise WorkflowConflict("Publishing platform version does not belong to Content")
    existing = db.get(PublishingTask, record_id)
    existing_status = canonical_status(existing.status) if existing else None
    if existing and existing_status == "PUBLISHED":
        if existing.content_id != content.id or existing.platform_version_id != version.id:
            raise WorkflowConflict("Published task version bindings are immutable")
        approval = db.get(ApprovalRecord, existing.approval_record_id) if existing.approval_record_id else None
        if approval is None:
            raise WorkflowConflict("Published task is missing its approval record")
    else:
        approval = active_approval(db, content.id, version.id, workspace_id)
        if approval is None:
            raise WorkflowConflict("Content version has not been approved or approval is stale")

    duplicate = db.scalar(select(PublishingTask).where(
        PublishingTask.workspace_id == workspace_id,
        PublishingTask.content_id == content.id,
        PublishingTask.platform_version_id == version.id,
        PublishingTask.scheduled_at == (values.get("scheduled_at") or ""),
    ))
    if duplicate and duplicate.id != record_id:
        return duplicate

    status = _validated_publish_status(values.get("status"))
    if existing:
        ensure_owned(existing, workspace_id, "PublishingTask")
        current_status = _validated_publish_status(existing_status)
        if status not in PUBLISH_TRANSITIONS[current_status]:
            raise WorkflowConflict(f"Illegal publishing transition: {current_status} -> {status}")
    if status == "PUBLISHED" and (not values.get("actual_published_at") or not values.get("url")):
        raise WorkflowConflict("Published tasks require actual_published_at and url")

    item_values = {
        **values,
        "workspace_id": workspace_id,
        "status": status,
        "approval_record_id": approval.id,
        "content_revision": content.revision,
        "version_snapshot": platform_snapshot(version),
        "platform": version.platform,
        "content_type": version.content_type,
    }
    if existing and existing_status == "PUBLISHED":
        item_values.update({
            "approval_record_id": existing.approval_record_id,
            "content_revision": existing.content_revision,
            "version_snapshot": existing.version_snapshot,
            "platform": existing.platform,
            "content_type": existing.content_type,
        })
    if existing:
        for key, value in item_values.items():
            setattr(existing, key, value)
        item = existing
        action = "content_published" if status == "PUBLISHED" and current_status != "PUBLISHED" else "publishing_status_changed"
    else:
        item = PublishingTask(id=record_id, **item_values)
        db.add(item)
        action = "publishing_task_created"
    if status == "PUBLISHED":
        content.status = "PUBLISHED"
    elif status == "SCHEDULED":
        content.status = "SCHEDULED"
    elif status in {"DRAFT", "READY"} and canonical_status(content.status) in APPROVED_STATUSES:
        content.status = "READY_TO_PUBLISH"
    log_activity(db, action, "PublishingTask", record_id, {"status": status, "platformVersionId": version.id, "approvalRecordId": approval.id}, workspace_id=workspace_id)
    return _finish(db, item, commit)


def start_tracking(db: Session, publishing_task_id: str, workspace_id: str = DEFAULT_WORKSPACE_ID, *, commit: bool = True) -> AnalyticsRecord:
    job = db.get(PublishingTask, publishing_task_id)
    ensure_owned(job, workspace_id, "PublishingTask")
    if canonical_status(job.status) != "PUBLISHED":
        raise WorkflowConflict("Only Published tasks can start tracking")
    if not job.actual_published_at or not job.url:
        raise WorkflowConflict("Published task is missing actual_published_at or url")
    existing = db.scalar(select(AnalyticsRecord).where(AnalyticsRecord.publishing_task_id == job.id))
    if existing:
        return existing
    item = AnalyticsRecord(
        id=f"analytics_{job.id}",
        workspace_id=workspace_id,
        publishing_task_id=job.id,
        content_id=job.content_id,
        platform=job.platform,
        content_type=job.content_type,
        tracking_status="TRACKING",
        raw={"trackingStartedAt": utcnow().isoformat()},
    )
    db.add(item)
    content = db.get(Content, job.content_id)
    ensure_owned(content, workspace_id, "Content")
    content.status = "TRACKING"
    log_activity(db, "tracking_started", "PublishingTask", job.id, {"analyticsRecordId": item.id}, workspace_id=workspace_id)
    return _finish(db, item, commit)


def save_analytics(db: Session, record_id: str, values: dict[str, Any], *, commit: bool = True) -> AnalyticsRecord:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    job = db.get(PublishingTask, values.get("publishing_task_id")) if values.get("publishing_task_id") else None
    ensure_owned(job, workspace_id, "PublishingTask")
    if canonical_status(job.status) != "PUBLISHED":
        raise WorkflowConflict("Analytics requires a Published task")
    if values.get("content_id") and values.get("content_id") != job.content_id:
        raise WorkflowConflict("Analytics Content does not match PublishingTask")
    existing_for_job = db.scalar(select(AnalyticsRecord).where(AnalyticsRecord.publishing_task_id == job.id))
    existing = db.get(AnalyticsRecord, record_id)
    if existing_for_job and existing_for_job.id != record_id:
        existing = existing_for_job
    item_values = {
        **values,
        "workspace_id": workspace_id,
        "publishing_task_id": job.id,
        "content_id": job.content_id,
        "platform": job.platform,
        "content_type": job.content_type,
        "tracking_status": canonical_status(values.get("tracking_status"), "NOT_STARTED"),
        "raw": {**((existing.raw if existing else {}) or {}), **(values.get("raw") or {})},
    }
    if existing:
        ensure_owned(existing, workspace_id, "AnalyticsRecord")
        prior_review = existing.performance_analysis
        for key, value in item_values.items():
            setattr(existing, key, value)
        item = existing
        action = "performance_review_generated" if item.performance_analysis and item.performance_analysis != prior_review else "analytics_updated"
    else:
        item = AnalyticsRecord(id=record_id, **item_values)
        db.add(item)
        action = "analytics_created"
    metrics = {
        "views": max(0, int(values.get("views") or 0)),
        "likes": max(0, int(values.get("likes") or 0)),
        "comments": max(0, int(values.get("comments") or 0)),
        "shares": max(0, int(values.get("shares") or 0)),
        "saves": max(0, int(values.get("saves") or 0)),
        "followersGained": max(0, int(values.get("followers_gained") or 0)),
    }
    if any(metrics.values()) and not (values.get("raw") or {}).get("sourceSnapshotId"):
        snapshot_id = f"track_{job.id}_manual_{stable_hash({'statsDate': values.get('stats_date'), 'metrics': metrics})[:12]}"
        if db.get(TrackingSnapshot, snapshot_id) is None:
            next_sequence = (db.scalar(select(func.max(TrackingSnapshot.sequence)).where(
                TrackingSnapshot.publishing_task_id == job.id,
                TrackingSnapshot.checkpoint_id == "manual",
            )) or 0) + 1
            db.add(TrackingSnapshot(
                id=snapshot_id,
                workspace_id=workspace_id,
                publishing_task_id=job.id,
                analytics_record_id=item.id,
                checkpoint_id="manual",
                sequence=next_sequence,
                recorded_at=utcnow(),
                label="Manual analytics update",
                status="DONE",
                stats_date=values.get("stats_date") or "",
                metrics=metrics,
                raw={"source": "analytics_update"},
            ))
            log_activity(db, "tracking_snapshot_created", "TrackingSnapshot", snapshot_id, {"publishingTaskId": job.id, "checkpointId": "manual", "sequence": next_sequence}, workspace_id=workspace_id)
    log_activity(db, action, "AnalyticsRecord", item.id, {"publishingTaskId": job.id}, workspace_id=workspace_id)
    return _finish(db, item, commit)


def append_tracking_snapshot(db: Session, record_id: str, values: dict[str, Any], *, commit: bool = True) -> TrackingSnapshot:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    job = db.get(PublishingTask, values.get("publishing_task_id"))
    ensure_owned(job, workspace_id, "PublishingTask")
    if canonical_status(job.status) != "PUBLISHED":
        raise WorkflowConflict("Tracking snapshot requires a Published task")
    analytics = db.get(AnalyticsRecord, values.get("analytics_record_id")) if values.get("analytics_record_id") else None
    ensure_owned(analytics, workspace_id, "AnalyticsRecord")
    if analytics.publishing_task_id != job.id:
        raise WorkflowConflict("TrackingSnapshot AnalyticsRecord does not match PublishingTask")

    existing = db.get(TrackingSnapshot, record_id)
    if existing:
        comparable = {
            "publishing_task_id": existing.publishing_task_id,
            "analytics_record_id": existing.analytics_record_id,
            "checkpoint_id": existing.checkpoint_id,
            "status": existing.status,
            "stats_date": existing.stats_date,
            "metrics": existing.metrics,
        }
        requested = {
            "publishing_task_id": values.get("publishing_task_id"),
            "analytics_record_id": values.get("analytics_record_id"),
            "checkpoint_id": values.get("checkpoint_id") or "",
            "status": canonical_status(values.get("status"), "DONE"),
            "stats_date": values.get("stats_date") or "",
            "metrics": values.get("metrics") or {},
        }
        if stable_hash(comparable) != stable_hash(requested):
            raise WorkflowConflict("Tracking snapshots are immutable; append a new snapshot")
        return existing

    checkpoint_id = values.get("checkpoint_id") or "manual"
    last_sequence = db.scalar(select(func.max(TrackingSnapshot.sequence)).where(
        TrackingSnapshot.publishing_task_id == job.id,
        TrackingSnapshot.checkpoint_id == checkpoint_id,
    )) or 0
    item_values = {
        **values,
        "workspace_id": workspace_id,
        "checkpoint_id": checkpoint_id,
        "sequence": last_sequence + 1,
        "recorded_at": values.get("recorded_at") or utcnow(),
        "status": canonical_status(values.get("status"), "DONE"),
    }
    item = TrackingSnapshot(id=record_id, **item_values)
    db.add(item)
    metrics = values.get("metrics") or {}
    for source_key, target_key in (
        ("views", "views"),
        ("likes", "likes"),
        ("comments", "comments"),
        ("shares", "shares"),
        ("saves", "saves"),
        ("followersGained", "followers_gained"),
        ("followers_gained", "followers_gained"),
    ):
        if source_key in metrics:
            setattr(analytics, target_key, max(0, int(metrics.get(source_key) or 0)))
    analytics.stats_date = values.get("stats_date") or metrics.get("statsDate") or analytics.stats_date
    analytics.tracking_status = "TRACKING"
    analytics.raw = {**(analytics.raw or {}), "latestSnapshotId": record_id}
    log_activity(db, "tracking_snapshot_created", "TrackingSnapshot", record_id, {"publishingTaskId": job.id, "checkpointId": checkpoint_id, "sequence": item.sequence}, workspace_id=workspace_id)
    log_activity(db, "analytics_updated", "AnalyticsRecord", analytics.id, {"sourceSnapshotId": record_id}, workspace_id=workspace_id)
    return _finish(db, item, commit)


def save_experience(db: Session, record_id: str, values: dict[str, Any], *, commit: bool = True) -> ExperienceRecord:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    job = db.get(PublishingTask, values.get("publishing_task_id")) if values.get("publishing_task_id") else None
    analytics = db.get(AnalyticsRecord, values.get("analytics_record_id")) if values.get("analytics_record_id") else None
    ensure_owned(job, workspace_id, "PublishingTask")
    ensure_owned(analytics, workspace_id, "AnalyticsRecord")
    if analytics.publishing_task_id != job.id:
        raise WorkflowConflict("Experience AnalyticsRecord does not match PublishingTask")
    if values.get("content_id") and values.get("content_id") != job.content_id:
        raise WorkflowConflict("Experience Content does not match PublishingTask")
    if values.get("platform_version_id") and values.get("platform_version_id") != job.platform_version_id:
        raise WorkflowConflict("Experience PlatformVersion does not match PublishingTask")
    existing_for_job = db.scalar(select(ExperienceRecord).where(ExperienceRecord.publishing_task_id == job.id))
    existing = db.get(ExperienceRecord, record_id) or existing_for_job
    item_values = {**values, "workspace_id": workspace_id, "content_id": job.content_id, "platform": job.platform, "content_type": job.content_type}
    if existing:
        for key, value in item_values.items():
            setattr(existing, key, value)
        item = existing
    else:
        item = ExperienceRecord(id=record_id, **item_values)
        db.add(item)
    log_activity(db, "performance_review_generated", "ExperienceRecord", item.id, {"publishingTaskId": job.id}, workspace_id=workspace_id)
    return _finish(db, item, commit)


def validate_knowledge_links(db: Session, values: dict[str, Any]) -> None:
    workspace_id = values.get("workspace_id") or DEFAULT_WORKSPACE_ID
    ensure_workspace(db, workspace_id)
    if values.get("topic_id"):
        ensure_owned(db.get(Topic, values["topic_id"]), workspace_id, "Topic")
    if values.get("content_id"):
        content = db.get(Content, values["content_id"])
        ensure_owned(content, workspace_id, "Content")
        if values.get("topic_id") and content.topic_id and content.topic_id != values["topic_id"]:
            raise WorkflowConflict("Knowledge Topic and Content relationship is inconsistent")


def assert_knowledge_type_boundary(item: KnowledgeEntry) -> None:
    if item.knowledge_type == "Fact" and not item.source:
        raise WorkflowConflict("Fact knowledge requires a source")
