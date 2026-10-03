"""PostgreSQL-backed durable queue and lease recovery services."""
from datetime import timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .activity import log_activity
from . import execution
from .models import ExecutionJob, ExternalCallAttempt, ExternalCallReceipt, GenerationRequest
from .workflow import WorkflowConflict, ensure_owned, stable_hash, utcnow

SUBMIT = "generation.submit"
POLL = "generation.poll"
CANCEL = "generation.cancel"
RECONCILE = "generation.reconcile"
JOB_TYPES = {SUBMIT, POLL, CANCEL, RECONCILE}


def _now(value=None):
    return value or utcnow()


def _aware(value):
    return value.replace(tzinfo=timezone.utc) if value and value.tzinfo is None else value


def _owned(db, cls, id, workspace_id, *, lock=False):
    query = select(cls).where(cls.id == id)
    if lock:
        query = query.with_for_update().execution_options(populate_existing=True)
    item = db.scalar(query)
    ensure_owned(item, workspace_id, cls.__name__)
    return item


def _log(db, action, job, details=None):
    log_activity(db, action, "ExecutionJob", job.id, details or {}, workspace_id=job.workspace_id)


def _enqueue(db: Session, request: GenerationRequest, job_type: str, idempotency_key: str,
             payload: dict | None = None, *, priority: int = 0, available_at=None,
             max_attempts: int = 3) -> ExecutionJob:
    if job_type not in JOB_TYPES:
        raise WorkflowConflict("Unsupported execution job type")
    execution._validate_config(payload or {})
    existing = db.scalar(select(ExecutionJob).where(ExecutionJob.idempotency_key == idempotency_key))
    if existing:
        ensure_owned(existing, request.workspace_id, "ExecutionJob")
        return existing
    job = ExecutionJob(
        id="job_" + stable_hash(idempotency_key), workspace_id=request.workspace_id,
        job_type=job_type, subject_type="GenerationRequest", subject_id=request.id,
        generation_request_id=request.id, idempotency_key=idempotency_key,
        payload=payload or {}, status="queued", priority=priority,
        available_at=_now(available_at), attempt_count=0, max_attempts=max(1, max_attempts),
        lease_owner="", last_error="",
    )
    db.add(job)
    db.flush()
    _log(db, "job_enqueued", job, {"jobType": job_type, "requestId": request.id})
    return job


def enqueue_generation_request(db: Session, request_id: str, workspace_id: str = "default",
                               *, priority: int = 0, max_attempts: int = 3) -> ExecutionJob:
    request = _owned(db, GenerationRequest, request_id, workspace_id, lock=True)
    if request.status in {"succeeded", "unknown", "cancelled", "submitting", "submitted", "polling"}:
        raise WorkflowConflict(f"GenerationRequest cannot be enqueued from {request.status}")
    key = f"generation.submit:{request.id}"
    existing = db.scalar(select(ExecutionJob).where(ExecutionJob.idempotency_key == key))
    if existing and existing.status in {"queued", "running", "succeeded"}:
        return existing
    if request.status in {"created", "failed"}:
        execution.transition_generation_request(db, request.id, workspace_id, "queued", commit=False)
    if existing:
        # Explicit re-enqueue after a confirmed failure receives a fresh technical budget.
        existing.status = "queued"
        existing.available_at = utcnow()
        existing.max_attempts += max(1, max_attempts)
        existing.lease_owner = ""
        existing.lease_expires_at = None
        existing.heartbeat_at = None
        existing.completed_at = None
        existing.last_error = ""
        _log(db, "job_retried", existing, {"manual": True})
        job = existing
    else:
        job = _enqueue(db, request, SUBMIT, key, priority=priority, max_attempts=max_attempts)
    db.commit()
    return job


def enqueue_poll(db: Session, request: GenerationRequest, sequence: int, *, available_at,
                 delay_seconds: int, commit: bool = False) -> ExecutionJob:
    key = f"generation.poll:{request.id}:{sequence}"
    job = _enqueue(db, request, POLL, key,
        {"poll_sequence": sequence, "delay_seconds": delay_seconds},
        available_at=available_at, max_attempts=3)
    log_activity(db, "polling_scheduled", "GenerationRequest", request.id,
        {"jobId": job.id, "sequence": sequence, "availableAt": available_at.isoformat()},
        workspace_id=request.workspace_id)
    if commit:
        db.commit()
    return job


def enqueue_cancel(db: Session, request: GenerationRequest, *, commit: bool = False) -> ExecutionJob:
    job = _enqueue(db, request, CANCEL, f"generation.cancel:{request.id}", priority=100, max_attempts=2)
    if commit:
        db.commit()
    return job


def enqueue_reconcile(db: Session, request_id: str, workspace_id: str = "default") -> ExecutionJob:
    request = _owned(db, GenerationRequest, request_id, workspace_id, lock=True)
    receipt = _owned(db, ExternalCallReceipt, request.receipt_id, workspace_id, lock=True)
    if request.status != "unknown" or receipt.status != "unknown":
        raise WorkflowConflict("Only an unknown provider outcome can be reconciled")
    job = _enqueue(db, request, RECONCILE, f"generation.reconcile:{request.id}", priority=100, max_attempts=2)
    db.commit()
    return job


def claim_next_job(db: Session, worker_id: str, *, lease_seconds: int = 30, now=None) -> ExecutionJob | None:
    if not worker_id.strip():
        raise WorkflowConflict("Worker ID is required")
    stamp = _now(now)
    job = db.scalar(
        select(ExecutionJob).where(
            ExecutionJob.status == "queued", ExecutionJob.available_at <= stamp
        ).order_by(ExecutionJob.priority.desc(), ExecutionJob.available_at, ExecutionJob.created_at)
        .with_for_update(skip_locked=True).limit(1).execution_options(populate_existing=True)
    )
    if not job:
        db.rollback()
        return None
    job.status = "running"
    job.attempt_count += 1
    job.lease_owner = worker_id
    job.heartbeat_at = stamp
    job.lease_expires_at = stamp + timedelta(seconds=max(1, lease_seconds))
    job.started_at = job.started_at or stamp
    _log(db, "job_claimed", job, {"worker": worker_id, "attempt": job.attempt_count})
    db.commit()
    db.refresh(job)
    return job


def heartbeat(db: Session, job_id: str, worker_id: str, *, lease_seconds: int = 30, now=None) -> ExecutionJob:
    stamp = _now(now)
    job = db.scalar(select(ExecutionJob).where(ExecutionJob.id == job_id).with_for_update().execution_options(populate_existing=True))
    if not job or job.status != "running" or job.lease_owner != worker_id:
        raise WorkflowConflict("Worker does not own this running job")
    if not job.lease_expires_at or _aware(job.lease_expires_at) <= stamp:
        raise WorkflowConflict("Job lease already expired")
    job.heartbeat_at = stamp
    job.lease_expires_at = stamp + timedelta(seconds=max(1, lease_seconds))
    db.commit()
    return job


def _leased_job(db, job_id, worker_id):
    job = db.scalar(select(ExecutionJob).where(ExecutionJob.id == job_id).with_for_update().execution_options(populate_existing=True))
    if not job or job.status != "running" or job.lease_owner != worker_id:
        raise WorkflowConflict("Worker does not own this running job")
    if not job.lease_expires_at or _aware(job.lease_expires_at) <= utcnow():
        raise WorkflowConflict("Job lease expired")
    return job


def succeed_job(db, job_id, worker_id, *, commit=True):
    job = _leased_job(db, job_id, worker_id)
    job.status = "succeeded"
    job.completed_at = utcnow()
    job.lease_owner = ""
    job.lease_expires_at = None
    _log(db, "job_succeeded", job)
    db.commit() if commit else db.flush()
    return job


def fail_job(db, job_id, worker_id, error, *, dead=False, commit=True):
    job = _leased_job(db, job_id, worker_id)
    job.status = "dead" if dead else "failed"
    job.last_error = str(error)
    job.completed_at = utcnow()
    job.lease_owner = ""
    job.lease_expires_at = None
    _log(db, "job_dead" if dead else "job_failed", job, {"error": str(error)})
    db.commit() if commit else db.flush()
    return job


def retry_job(db, job_id, worker_id, error, *, now=None, commit=True):
    job = _leased_job(db, job_id, worker_id)
    job.last_error = str(error)
    job.lease_owner = ""
    job.lease_expires_at = None
    job.heartbeat_at = None
    if job.attempt_count >= job.max_attempts:
        job.status = "dead"
        job.completed_at = _now(now)
        _log(db, "job_dead", job, {"error": str(error), "attempt": job.attempt_count})
    else:
        delay = min(300, 2 ** job.attempt_count)
        job.status = "queued"
        job.available_at = _now(now) + timedelta(seconds=delay)
        _log(db, "job_retried", job, {"error": str(error), "delaySeconds": delay, "attempt": job.attempt_count})
    db.commit() if commit else db.flush()
    return job


def manual_retry(db: Session, job_id: str, workspace_id: str) -> ExecutionJob:
    job = _owned(db, ExecutionJob, job_id, workspace_id, lock=True)
    if job.status not in {"failed", "dead"}:
        raise WorkflowConflict("Only failed or dead jobs can be retried")
    request = _owned(db, GenerationRequest, job.generation_request_id, workspace_id, lock=True)
    receipt = _owned(db, ExternalCallReceipt, request.receipt_id, workspace_id, lock=True)
    reconciliation_retry = job.job_type == RECONCILE and request.status == "unknown" and receipt.status == "unknown"
    if not reconciliation_retry and (request.status in {"unknown", "succeeded", "cancelled"} or receipt.status in {"unknown", "completed"}):
        raise WorkflowConflict("This outcome is not safe to retry")
    if job.job_type == SUBMIT and request.status == "failed":
        execution.transition_generation_request(db, request.id, workspace_id, "queued", commit=False)
    job.status = "queued"
    job.max_attempts += max(1, job.max_attempts)
    job.available_at = utcnow()
    job.completed_at = None
    job.last_error = ""
    job.lease_owner = ""
    job.lease_expires_at = None
    _log(db, "job_retried", job, {"manual": True})
    db.commit()
    return job


def cancel_request(db: Session, request_id: str, workspace_id: str) -> dict:
    request = _owned(db, GenerationRequest, request_id, workspace_id, lock=True)
    jobs = list(db.scalars(select(ExecutionJob).where(ExecutionJob.generation_request_id == request.id).with_for_update()).all())
    if request.status in {"created", "queued", "failed"}:
        execution.transition_generation_request(db, request.id, workspace_id, "cancelled", commit=False)
        for job in jobs:
            if job.status == "queued":
                job.status = "cancelled"
                job.completed_at = utcnow()
                _log(db, "job_cancelled", job, {"reason": "request_cancelled_before_dispatch"})
        db.commit()
        return {"request": request, "job": None}
    if request.status in {"submitted", "polling"}:
        job = enqueue_cancel(db, request)
        db.commit()
        return {"request": request, "job": job}
    raise WorkflowConflict(f"GenerationRequest cannot be cancelled from {request.status}")


def recover_expired_leases(db: Session, *, now=None) -> dict:
    stamp = _now(now)
    jobs = list(db.scalars(select(ExecutionJob).where(
        ExecutionJob.status == "running", ExecutionJob.lease_expires_at <= stamp
    ).order_by(ExecutionJob.created_at).with_for_update(skip_locked=True).execution_options(populate_existing=True)).all())
    summary = {"requeued": 0, "unknown": 0, "completed": 0, "dead": 0}
    for job in jobs:
        outcome = "recovered"
        request = _owned(db, GenerationRequest, job.generation_request_id, job.workspace_id, lock=True)
        receipt = _owned(db, ExternalCallReceipt, request.receipt_id, job.workspace_id, lock=True)
        active_attempt = db.scalar(select(ExternalCallAttempt).where(
            ExternalCallAttempt.receipt_id == receipt.id, ExternalCallAttempt.status == "running"
        ).with_for_update())
        if request.status == "succeeded":
            job.status = "succeeded"
            job.completed_at = stamp
            summary["completed"] += 1
            outcome = "completed"
        elif job.job_type == SUBMIT and request.status in {"submitted", "polling"} and receipt.status == "received":
            poll_jobs = list(db.scalars(select(ExecutionJob).where(
                ExecutionJob.generation_request_id == request.id, ExecutionJob.job_type == POLL
            ).with_for_update()).all())
            if not any(item.status in {"queued", "running"} for item in poll_jobs):
                sequences = [int((item.payload or {}).get("poll_sequence", 0)) for item in poll_jobs]
                sequence = max(sequences, default=0) + 1
                enqueue_poll(db, request, sequence, available_at=stamp, delay_seconds=0)
            job.status = "succeeded"
            job.completed_at = stamp
            summary["completed"] += 1
            outcome = "completed"
        elif (job.job_type == SUBMIT and active_attempt) or job.job_type == CANCEL:
            if active_attempt:
                execution.mark_unknown(db, receipt.id, job.workspace_id, attempt_id=active_attempt.id,
                    error="Worker lease expired after dispatch", commit=False)
            elif receipt.status == "received":
                # No active submit Attempt for cancel, but provider cancellation may have been sent.
                execution.mark_unknown(db, receipt.id, job.workspace_id,
                    error="Worker lease expired during provider cancellation", commit=False)
            if request.status != "unknown":
                execution.transition_generation_request(db, request.id, job.workspace_id, "unknown",
                    error="Worker crashed after provider dispatch", commit=False)
            job.status = "failed"
            job.last_error = "Unsafe in-flight provider outcome; reconciliation required"
            job.completed_at = stamp
            log_activity(db, "provider_unknown", "GenerationRequest", request.id,
                {"jobId": job.id}, workspace_id=job.workspace_id)
            summary["unknown"] += 1
            outcome = "unknown"
        elif job.job_type == RECONCILE and request.status == "unknown" and receipt.status == "unknown":
            if job.attempt_count >= job.max_attempts:
                job.status = "dead"
                job.last_error = "Reconciliation lease expired"
                job.completed_at = stamp
                summary["dead"] += 1
                outcome = "dead"
            else:
                job.status = "queued"
                job.available_at = stamp + timedelta(seconds=min(300, 2 ** job.attempt_count))
                summary["requeued"] += 1
                outcome = "requeued"
        elif request.status in {"unknown", "cancelled"} or receipt.status == "unknown":
            job.status = "failed"
            job.last_error = "Request is not safely retryable"
            job.completed_at = stamp
            summary["unknown"] += 1
            outcome = "unknown"
        elif job.attempt_count >= job.max_attempts:
            job.status = "dead"
            job.last_error = "Lease expired before safe completion"
            job.completed_at = stamp
            summary["dead"] += 1
            outcome = "dead"
        else:
            job.status = "queued"
            job.available_at = stamp + timedelta(seconds=min(300, 2 ** job.attempt_count))
            summary["requeued"] += 1
            outcome = "requeued"
        job.lease_owner = ""
        job.lease_expires_at = None
        job.heartbeat_at = None
        _log(db, "lease_recovered", job, {"outcome": outcome})
    db.commit()
    return summary


def list_jobs(db, workspace_id, request_id=None):
    query = select(ExecutionJob).where(ExecutionJob.workspace_id == workspace_id)
    if request_id:
        query = query.where(ExecutionJob.generation_request_id == request_id)
    return list(db.scalars(query.order_by(ExecutionJob.created_at.desc())).all())
