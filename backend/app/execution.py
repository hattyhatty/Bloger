"""Durable execution bookkeeping only: no transport, worker or automatic retry.

Each public mutation is one transaction. Finished attempts and request input
snapshots are append-only through this service. Unknown outcomes require explicit
provider evidence to reconcile; they must never be interpreted as retryable errors.
"""
from datetime import timezone
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .activity import log_activity
from .models import (Content, Topic, KnowledgeEntry, VideoProductionPlan, VideoShot,
                     VideoStoryboard, VideoGenerationPrompt, ExternalCallReceipt,
                     ExternalCallAttempt, GenerationRequest, VideoReferenceAsset,
                     VideoShotReferenceLink)
from .prompt_registry import PromptRegistry
from .workflow import WorkflowConflict, ensure_owned, stable_hash, utcnow

SUBJECTS = {cls.__name__: cls for cls in (Content, Topic, KnowledgeEntry, VideoProductionPlan, VideoShot, VideoGenerationPrompt)}
TRANSITIONS = {
    "created": {"queued", "submitting", "cancelled"},
    "queued": {"submitting", "failed", "cancelled"},
    "submitting": {"queued", "submitted", "succeeded", "failed", "unknown"},
    "submitted": {"polling", "succeeded", "failed", "unknown", "cancelled"},
    "polling": {"succeeded", "failed", "unknown", "cancelled"},
    "failed": {"queued", "cancelled"},
    "unknown": {"submitted", "succeeded", "failed"},
    "succeeded": set(), "cancelled": set(),
}


def logical_key(*, workspace_id, service, purpose, subject_type, subject_id,
                input_revision, input_hash, provider, model, prompt_key,
                prompt_version, prompt_hash, artifact_revision, config_hash):
    return stable_hash({"schema": 1, "workspace": workspace_id, "service": service,
        "purpose": purpose, "subject": [subject_type, subject_id],
        "input": [str(input_revision), input_hash], "provider": provider, "model": model,
        "template": [prompt_key, prompt_version, prompt_hash],
        "artifact_revision": artifact_revision, "config_hash": config_hash})


def _owned(db, cls, id, workspace_id):
    item = db.scalar(select(cls).where(cls.id == id).with_for_update().execution_options(populate_existing=True))
    ensure_owned(item, workspace_id, cls.__name__)
    return item


def _log(db, action, item, details=None):
    log_activity(db, action, type(item).__name__, item.id, details or {}, workspace_id=item.workspace_id)


def _receipt(db, values):
    cls = SUBJECTS.get(values["subject_type"])
    if not cls:
        raise WorkflowConflict("Unsupported receipt subject type")
    # The subject lock serializes duplicate creation (including concurrent retries).
    _owned(db, cls, values["subject_id"], values["workspace_id"])
    template = PromptRegistry.get(values["prompt_key"])
    config = values.get("config") or {}
    _validate_config(config)
    _validate_config(values.get("request_summary") or {})
    digest = stable_hash(config)
    key = logical_key(**{name: values[name] for name in (
        "workspace_id", "service", "purpose", "subject_type", "subject_id",
        "input_revision", "input_hash", "provider", "model")},
        prompt_key=template.prompt_key, prompt_version=template.version,
        prompt_hash=template.hash, artifact_revision=values.get("artifact_revision", 0), config_hash=digest)
    item = db.scalar(select(ExternalCallReceipt).where(ExternalCallReceipt.logical_key == key))
    if item:
        _log(db, "external_receipt_reused", item)
        return item
    item = ExternalCallReceipt(id="receipt_" + key, logical_key=key,
        **{name: values[name] for name in ("workspace_id", "service", "provider", "model",
            "purpose", "subject_type", "subject_id", "input_revision", "input_hash")},
        prompt_key=template.prompt_key, prompt_version=template.version, prompt_hash=template.hash,
        config_hash=digest, status="pending", request_summary={
            "input": values.get("request_summary") or {}, "template_content": template.content,
            "artifact_revision": values.get("artifact_revision", 0), "config": config})
    db.add(item)
    db.flush()
    _log(db, "external_receipt_created", item)
    return item


def _validate_config(config):
    # Credentials belong to provider configuration, never persisted execution input.
    def visit(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key.lower().replace("-", "_") in {"api_key", "apikey", "token", "access_token", "refresh_token", "password", "authorization", "secret", "client_secret"}:
                    raise WorkflowConflict("Credentials are not allowed in execution config")
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    visit(config)
    try:
        json.dumps(config, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise WorkflowConflict("Execution config must contain finite JSON values") from exc


def create_or_get_receipt(db: Session, values: dict) -> ExternalCallReceipt:
    item = _receipt(db, values)
    db.commit()
    return item


def start_attempt(db: Session, receipt_id: str, workspace_id: str, *, commit: bool = True) -> ExternalCallAttempt:
    linked = db.scalar(select(GenerationRequest).where(GenerationRequest.receipt_id == receipt_id))
    if linked:
        linked = _owned(db, GenerationRequest, linked.id, workspace_id)
        if linked.status not in {"created", "queued"}:
            raise WorkflowConflict("GenerationRequest must be created or queued before starting an attempt")
    item = _owned(db, ExternalCallReceipt, receipt_id, workspace_id)
    if item.status not in {"pending", "failed"}:
        raise WorkflowConflict("Receipt is not retryable; unknown requires provider reconciliation")
    attempts = list(db.scalars(select(ExternalCallAttempt).where(ExternalCallAttempt.receipt_id == item.id)).all())
    if any(attempt.status == "running" for attempt in attempts):
        raise WorkflowConflict("An attempt is already running; resolve a crash as unknown before proceeding")
    number = max((attempt.attempt_number for attempt in attempts), default=0) + 1
    attempt = ExternalCallAttempt(id=f"{item.id}_a{number}", receipt_id=item.id, attempt_number=number, status="running")
    item.status = "pending"
    item.response_payload = {}
    item.provider_request_id = ""
    item.received_at = None
    item.completed_at = None
    item.usage = {}
    item.cost = None
    item.currency = ""
    db.add(attempt)
    db.flush()
    _log(db, "external_attempt_started", item, {"attemptId": attempt.id, "number": number})
    if commit:
        db.commit()
    else:
        db.flush()
    return attempt


def _mark(db, receipt_id, workspace_id, target, *, attempt_id=None, provider_request_id="",
          response_payload=None, usage=None, cost=None, currency="", error="", reconciliation="", commit=True):
    item = _owned(db, ExternalCallReceipt, receipt_id, workspace_id)
    if item.status == target:
        # Duplicate acknowledgements are harmless, but must belong to this receipt.
        if attempt_id:
            attempt = db.get(ExternalCallAttempt, attempt_id)
            if not attempt or attempt.receipt_id != item.id:
                raise WorkflowConflict("Attempt belongs to another receipt")
            latest = db.scalar(select(ExternalCallAttempt).where(ExternalCallAttempt.receipt_id == item.id).order_by(ExternalCallAttempt.attempt_number.desc()).limit(1))
            if latest.id != attempt.id:
                raise WorkflowConflict("Stale attempt outcome rejected")
        return item
    allowed = {"pending": {"received", "completed", "failed", "unknown"},
        "received": {"completed", "failed", "unknown"},
        "unknown": {"received", "completed", "failed"}, "failed": set(), "completed": set()}
    if target not in allowed[item.status]:
        raise WorkflowConflict("Invalid receipt transition")
    if item.status == "unknown" and not (reconciliation.strip() and provider_request_id.strip()):
        raise WorkflowConflict("Unknown outcome requires explicit provider ID and reconciliation evidence")
    running = db.scalar(select(ExternalCallAttempt).where(
        ExternalCallAttempt.receipt_id == item.id, ExternalCallAttempt.status == "running"))
    if running:
        if attempt_id != running.id:
            raise WorkflowConflict("Active attempt ID required; stale attempt outcome rejected")
        now = utcnow()
        running.status = target
        running.finished_at = now
        started = running.started_at.replace(tzinfo=timezone.utc) if running.started_at.tzinfo is None else running.started_at
        running.latency_ms = max(0, int((now - started).total_seconds() * 1000))
        running.provider_request_id = provider_request_id
        running.error = error
        running.usage = usage or {}
        running.cost = cost
    elif item.status == "pending":
        raise WorkflowConflict("Start an attempt before recording an outcome")
    elif attempt_id:
        attempt = db.get(ExternalCallAttempt, attempt_id)
        if not attempt or attempt.receipt_id != item.id:
            raise WorkflowConflict("Attempt belongs to another receipt")
        latest = db.scalar(select(ExternalCallAttempt).where(ExternalCallAttempt.receipt_id == item.id).order_by(ExternalCallAttempt.attempt_number.desc()).limit(1))
        if latest.id != attempt.id:
            raise WorkflowConflict("Stale attempt outcome rejected")
    item.status = target
    item.response_payload = response_payload or ({"error": error} if error else {})
    item.provider_request_id = provider_request_id or item.provider_request_id
    item.usage = usage if usage is not None else item.usage
    item.cost = cost if cost is not None else item.cost
    item.currency = currency or item.currency
    if target == "received":
        item.received_at = utcnow()
    if target == "completed":
        item.received_at = item.received_at or utcnow()
        item.completed_at = utcnow()
    _log(db, "external_receipt_" + target, item, {"attemptId": attempt_id, "reconciliation": reconciliation})
    if commit:
        db.commit()
    else:
        db.flush()
    return item


def mark_received(db, receipt_id, workspace_id, **values):
    return _mark(db, receipt_id, workspace_id, "received", **values)


def mark_completed(db, receipt_id, workspace_id, **values):
    return _mark(db, receipt_id, workspace_id, "completed", **values)


def mark_failed(db, receipt_id, workspace_id, **values):
    return _mark(db, receipt_id, workspace_id, "failed", **values)


def mark_unknown(db, receipt_id, workspace_id, **values):
    return _mark(db, receipt_id, workspace_id, "unknown", **values)


def mark_attempt_not_accepted(db, receipt_id, workspace_id, attempt_id, error, *, commit=True):
    """Close an attempt after a definitive provider rejection without failing its receipt."""
    item = _owned(db, ExternalCallReceipt, receipt_id, workspace_id)
    attempt = db.get(ExternalCallAttempt, attempt_id)
    if not attempt or attempt.receipt_id != item.id or attempt.status != "running":
        raise WorkflowConflict("Active attempt ID required")
    now = utcnow()
    attempt.status = "failed"
    attempt.finished_at = now
    started = attempt.started_at.replace(tzinfo=timezone.utc) if attempt.started_at.tzinfo is None else attempt.started_at
    attempt.latency_ms = max(0, int((now - started).total_seconds() * 1000))
    attempt.error = str(error)
    item.status = "pending"
    item.response_payload = {"error": str(error)}
    _log(db, "external_attempt_not_accepted", item, {"attemptId": attempt.id})
    db.commit() if commit else db.flush()
    return attempt


def mark_pre_dispatch_failed(db, receipt_id, workspace_id, error, *, commit=True):
    """Record a definitive local/provider configuration rejection with no dispatched Attempt."""
    item = _owned(db, ExternalCallReceipt, receipt_id, workspace_id)
    running = db.scalar(select(ExternalCallAttempt).where(
        ExternalCallAttempt.receipt_id == item.id, ExternalCallAttempt.status == "running"))
    if running or item.status not in {"pending", "failed"}:
        raise WorkflowConflict("Pre-dispatch failure requires a pending receipt without an active attempt")
    item.status = "failed"
    item.response_payload = {"error": str(error)}
    _log(db, "external_receipt_failed", item, {"preDispatch": True})
    db.commit() if commit else db.flush()
    return item


def create_generation_request(db: Session, values: dict) -> GenerationRequest:
    from .video_planner import shot_snapshot, prompt_snapshot
    workspace = values.get("workspace_id", "default")
    # Match the planner's lock order: shot first, then prompt.
    prompt = db.get(VideoGenerationPrompt, values["prompt_id"])
    ensure_owned(prompt, workspace, "VideoGenerationPrompt")
    shot = _owned(db, VideoShot, prompt.shot_id, workspace)
    prompt = _owned(db, VideoGenerationPrompt, prompt.id, workspace)
    # Reorder takes a storyboard lock before updating shots. Do not take that
    # lock while holding a shot: it would invert the established lock order.
    storyboard = db.scalar(select(VideoStoryboard).where(VideoStoryboard.id == shot.storyboard_id).execution_options(populate_existing=True))
    ensure_owned(storyboard, workspace, "VideoStoryboard")
    plan = db.get(VideoProductionPlan, storyboard.plan_id)
    ensure_owned(plan, workspace, "VideoProductionPlan")
    links = db.scalars(select(VideoShotReferenceLink).where(
        VideoShotReferenceLink.shot_id == shot.id,
        VideoShotReferenceLink.workspace_id == workspace,
    )).all()
    references = []
    for link in links:
        asset = db.get(VideoReferenceAsset, link.asset_id)
        ensure_owned(asset, workspace, "VideoReferenceAsset")
        references.append({"id": asset.id, "asset_type": asset.asset_type, "title": asset.title,
            "reference_url": asset.reference_url, "file_reference": asset.file_reference,
            "status": asset.status, "plan_content_revision": link.plan_content_revision})
    snapshot = {"plan_id": plan.id, "content_revision": plan.content_revision,
        "content_hash": plan.content_hash, "content_snapshot": plan.content_snapshot,
        "video_plan": {"target_platform": plan.target_platform,
            "target_duration_seconds": plan.target_duration_seconds,
            "content_format": plan.content_format, "visual_style": plan.visual_style,
            "aspect_ratio": plan.aspect_ratio},
        "storyboard_revision": storyboard.revision, "shot": shot_snapshot(shot),
        "prompt": prompt_snapshot(prompt), "consistency": {
            "character": storyboard.recurring_character_description, "clothing": storyboard.clothing,
            "environment": storyboard.environment, "visual_style": storyboard.visual_style,
            "reference_notes": storyboard.reference_notes}, "reference_assets": references}
    receipt = _receipt(db, {"workspace_id": workspace, "service": "video", "purpose": "video.generate",
        "subject_type": "VideoGenerationPrompt", "subject_id": prompt.id,
        "input_revision": str(plan.content_revision), "input_hash": stable_hash(snapshot),
        "artifact_revision": prompt.revision, "provider": values["provider"], "model": values.get("model", ""),
        "prompt_key": values.get("prompt_key", "video.generate"), "config": values.get("generation_config", {}),
        "request_summary": snapshot})
    item = db.scalar(select(GenerationRequest).where(GenerationRequest.logical_key == receipt.logical_key))
    if not item:
        item = GenerationRequest(id="generation_" + receipt.logical_key, workspace_id=workspace,
            plan_id=plan.id, shot_id=shot.id, prompt_id=prompt.id, prompt_revision=prompt.revision,
            provider=values["provider"], model=values.get("model", ""), generation_config=values.get("generation_config", {}),
            input_snapshot=snapshot, logical_key=receipt.logical_key, receipt_id=receipt.id, status="created")
        db.add(item)
        db.flush()
        _log(db, "generation_request_created", item, {"receiptId": receipt.id})
    db.commit()
    return item


def transition_generation_request(db, request_id, workspace_id, status, *, provider_job_id="", error="",
                                  provider_cancelled: bool = False, provider_not_accepted: bool = False,
                                  commit: bool = True):
    item = _owned(db, GenerationRequest, request_id, workspace_id)
    receipt = _owned(db, ExternalCallReceipt, item.receipt_id, workspace_id)
    if status == item.status:
        return item
    if status not in TRANSITIONS[item.status]:
        raise WorkflowConflict(f"Invalid GenerationRequest transition: {item.status} -> {status}")
    if status == "cancelled":
        running = db.scalar(select(ExternalCallAttempt).where(ExternalCallAttempt.receipt_id == receipt.id, ExternalCallAttempt.status == "running"))
        if not provider_cancelled and (running or receipt.status not in {"pending", "failed"}):
            raise WorkflowConflict("A dispatched or uncertain call cannot be cancelled as an unsent request")
    if item.status == "submitting" and status == "queued" and not provider_not_accepted:
        raise WorkflowConflict("Only a definitive provider rejection may return submitting to queued")
    required = {"submitted": {"received", "completed"}, "polling": {"received", "completed"},
        "succeeded": {"completed"}, "failed": {"failed"}, "unknown": {"unknown"}, "queued": {"pending", "failed"}}
    if status in required and receipt.status not in required[status]:
        raise WorkflowConflict("GenerationRequest outcome does not match receipt")
    if status == "submitting":
        active = db.scalar(select(ExternalCallAttempt).where(ExternalCallAttempt.receipt_id == receipt.id, ExternalCallAttempt.status == "running"))
        if receipt.status != "pending" or not active:
            raise WorkflowConflict("Submitting requires a running receipt attempt")
    if status in {"submitted", "polling"} and not (provider_job_id or item.provider_job_id):
        raise WorkflowConflict("Provider job ID is required")
    if provider_job_id and item.provider_job_id and provider_job_id != item.provider_job_id:
        raise WorkflowConflict("Provider job ID is immutable after submission")
    previous = item.status
    previous_job_id = item.provider_job_id
    if previous == "failed" and status == "queued":
        # A confirmed failure may retry; keep the old job in audit/attempt
        # history, while this request now tracks the new attempt's job.
        item.provider_job_id = ""
        item.submitted_at = None
        item.last_polled_at = None
    item.status = status
    item.provider_job_id = provider_job_id or item.provider_job_id
    item.error = error
    stamp = {"queued": "queued_at", "submitted": "submitted_at", "polling": "last_polled_at",
        "succeeded": "completed_at", "failed": "completed_at", "cancelled": "completed_at"}.get(status)
    if stamp:
        setattr(item, stamp, utcnow())
    if status in {"queued", "submitting"}:
        item.completed_at = None
    _log(db, "generation_request_state_changed", item, {"from": previous, "to": status, "previousJobId": previous_job_id, "jobId": item.provider_job_id})
    if commit:
        db.commit()
    else:
        db.flush()
    return item
