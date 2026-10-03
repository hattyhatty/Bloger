"""Thin execution API; all mutations are delegated to execution services."""
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import execution
from .database import get_db
from .models import ExternalCallReceipt, ExternalCallAttempt, GenerationRequest
from . import queue
from .workflow import ensure_owned

router = APIRouter(prefix="/api/execution", tags=["execution"])


class ReceiptIn(BaseModel):
    workspace_id: str = "default"
    service: str = Field(min_length=1, max_length=64)
    provider: str = Field(min_length=1, max_length=64)
    model: str = Field(default="", max_length=128)
    purpose: str = Field(min_length=1, max_length=128)
    subject_type: str
    subject_id: str
    input_revision: str = Field(max_length=128)
    input_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    prompt_key: str = "video.generate"
    artifact_revision: int = Field(default=0, ge=0)
    config: dict = Field(default_factory=dict)
    request_summary: dict = Field(default_factory=dict)


class WorkspaceIn(BaseModel):
    workspace_id: str = "default"


class OutcomeIn(WorkspaceIn):
    status: Literal["received", "completed", "failed", "unknown"]
    attempt_id: str | None = None
    provider_request_id: str = Field(default="", max_length=255)
    response_payload: dict | None = None
    usage: dict | None = None
    cost: str | None = Field(default=None, max_length=64)
    currency: str = Field(default="", max_length=16)
    error: str = ""
    reconciliation: str = ""


class GenerationIn(WorkspaceIn):
    prompt_id: str
    provider: str = Field(min_length=1, max_length=64)
    model: str = Field(default="", max_length=128)
    generation_config: dict = Field(default_factory=dict)
    prompt_key: str = "video.generate"


class TransitionIn(WorkspaceIn):
    status: Literal["created", "queued", "submitting", "submitted", "polling", "succeeded", "failed", "unknown", "cancelled"]
    provider_job_id: str = Field(default="", max_length=255)
    error: str = ""


class EnqueueIn(WorkspaceIn):
    priority: int = Field(default=0, ge=-100, le=100)
    max_attempts: int = Field(default=3, ge=1, le=20)


def document(item):
    return {column.name: getattr(item, column.name) for column in item.__table__.columns}


@router.post("/receipts")
def create_receipt(payload: ReceiptIn, db: Session = Depends(get_db)):
    return document(execution.create_or_get_receipt(db, payload.model_dump()))


@router.get("/receipts")
def receipts(workspace_id: str = "default", db: Session = Depends(get_db)):
    return [document(item) for item in db.scalars(select(ExternalCallReceipt).where(ExternalCallReceipt.workspace_id == workspace_id)).all()]


@router.get("/receipts/{receipt_id}")
def receipt_detail(receipt_id: str, workspace_id: str = "default", db: Session = Depends(get_db)):
    item = db.get(ExternalCallReceipt, receipt_id)
    ensure_owned(item, workspace_id, "ExternalCallReceipt")
    return {"receipt": document(item), "attempts": [document(attempt) for attempt in db.scalars(
        select(ExternalCallAttempt).where(ExternalCallAttempt.receipt_id == item.id).order_by(ExternalCallAttempt.attempt_number)).all()]}


@router.post("/receipts/{receipt_id}/attempts")
def attempt(receipt_id: str, payload: WorkspaceIn, db: Session = Depends(get_db)):
    return document(execution.start_attempt(db, receipt_id, payload.workspace_id))


@router.patch("/receipts/{receipt_id}/outcome")
def outcome(receipt_id: str, payload: OutcomeIn, db: Session = Depends(get_db)):
    values = payload.model_dump()
    status = values.pop("status")
    workspace = values.pop("workspace_id")
    return document(getattr(execution, "mark_" + status)(db, receipt_id, workspace, **values))


@router.post("/generation-requests")
def generation(payload: GenerationIn, db: Session = Depends(get_db)):
    return document(execution.create_generation_request(db, payload.model_dump()))


@router.get("/generation-requests")
def generations(workspace_id: str = "default", shot_id: str | None = None, db: Session = Depends(get_db)):
    query = select(GenerationRequest).where(GenerationRequest.workspace_id == workspace_id)
    if shot_id:
        query = query.where(GenerationRequest.shot_id == shot_id)
    return [document(item) for item in db.scalars(query).all()]


@router.get("/generation-requests/{request_id}")
def generation_detail(request_id: str, workspace_id: str = "default", db: Session = Depends(get_db)):
    item = db.get(GenerationRequest, request_id)
    ensure_owned(item, workspace_id, "GenerationRequest")
    return document(item)


@router.patch("/generation-requests/{request_id}/status")
def transition(request_id: str, payload: TransitionIn, db: Session = Depends(get_db)):
    values = payload.model_dump()
    if payload.status == "queued":
        queue.enqueue_generation_request(db, request_id, payload.workspace_id)
        item = db.get(GenerationRequest, request_id)
        ensure_owned(item, payload.workspace_id, "GenerationRequest")
        return document(item)
    return document(execution.transition_generation_request(db, request_id, **values))


@router.post("/generation-requests/{request_id}/enqueue")
def enqueue_request(request_id: str, payload: EnqueueIn, db: Session = Depends(get_db)):
    return document(queue.enqueue_generation_request(db, request_id, payload.workspace_id,
        priority=payload.priority, max_attempts=payload.max_attempts))


@router.get("/generation-requests/{request_id}/execution-state")
def execution_state(request_id: str, workspace_id: str = "default", db: Session = Depends(get_db)):
    request = db.get(GenerationRequest, request_id)
    ensure_owned(request, workspace_id, "GenerationRequest")
    receipt = db.get(ExternalCallReceipt, request.receipt_id)
    ensure_owned(receipt, workspace_id, "ExternalCallReceipt")
    attempts = db.scalars(select(ExternalCallAttempt).where(
        ExternalCallAttempt.receipt_id == receipt.id).order_by(ExternalCallAttempt.attempt_number)).all()
    jobs = queue.list_jobs(db, workspace_id, request_id)
    return {"request": document(request), "receipt": document(receipt),
        "attempts": [document(item) for item in attempts], "jobs": [document(item) for item in jobs]}


@router.get("/jobs")
def jobs(workspace_id: str = "default", request_id: str | None = None, db: Session = Depends(get_db)):
    return [document(item) for item in queue.list_jobs(db, workspace_id, request_id)]


@router.post("/jobs/{job_id}/retry")
def retry_job(job_id: str, payload: WorkspaceIn, db: Session = Depends(get_db)):
    return document(queue.manual_retry(db, job_id, payload.workspace_id))


@router.post("/generation-requests/{request_id}/cancel")
def cancel_request(request_id: str, payload: WorkspaceIn, db: Session = Depends(get_db)):
    result = queue.cancel_request(db, request_id, payload.workspace_id)
    return {"request": document(result["request"]), "job": document(result["job"]) if result["job"] else None}


@router.post("/generation-requests/{request_id}/reconcile")
def reconcile_request(request_id: str, payload: WorkspaceIn, db: Session = Depends(get_db)):
    return document(queue.enqueue_reconcile(db, request_id, payload.workspace_id))
