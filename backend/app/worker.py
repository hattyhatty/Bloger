"""Independent durable queue worker: ``python -m app.worker``.

The worker never runs inside FastAPI. One provider poll is one short durable job;
there is no provider-polling sleep loop.
"""
import argparse
import socket
import threading
import time
import uuid
from datetime import timedelta, timezone

from sqlalchemy import select

from .database import SessionLocal
from . import execution
from .models import ExecutionJob, ExternalCallReceipt, GenerationRequest
from .providers import ProviderError, get_video_provider
from .queue import (CANCEL, POLL, RECONCILE, SUBMIT, claim_next_job, enqueue_poll, fail_job,
                    heartbeat, recover_expired_leases, retry_job, succeed_job)
from .video_planner import add_generation_result
from .workflow import WorkflowConflict, ensure_owned, utcnow
from .activity import log_activity


class LeaseHeartbeat:
    """Refresh a claimed lease while a potentially slow adapter method is running."""

    def __init__(self, session_factory, job_id, worker_id, lease_seconds):
        self.session_factory = session_factory
        self.job_id = job_id
        self.worker_id = worker_id
        self.lease_seconds = lease_seconds
        self.stop_event = threading.Event()
        self.thread = None

    def __enter__(self):
        interval = max(0.25, self.lease_seconds / 3)

        def beat():
            while not self.stop_event.wait(interval):
                with self.session_factory() as db:
                    try:
                        heartbeat(db, self.job_id, self.worker_id, lease_seconds=self.lease_seconds)
                    except Exception:
                        db.rollback()
                        return

        self.thread = threading.Thread(target=beat, name=f"lease-{self.job_id}", daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=1)


def _load(db, job_id, worker_id):
    # Do not hold queue-row locks during provider I/O; the lease is the execution
    # right, and a separate connection must remain free to heartbeat it.
    job = db.scalar(select(ExecutionJob).where(ExecutionJob.id == job_id).execution_options(populate_existing=True))
    if not job or job.status != "running" or job.lease_owner != worker_id:
        raise WorkflowConflict("Worker does not own this running job")
    expires = job.lease_expires_at
    if expires and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if not expires or expires <= utcnow():
        raise WorkflowConflict("Job lease expired")
    request = db.scalar(select(GenerationRequest).where(GenerationRequest.id == job.generation_request_id).execution_options(populate_existing=True))
    ensure_owned(request, job.workspace_id, "GenerationRequest")
    receipt = db.scalar(select(ExternalCallReceipt).where(ExternalCallReceipt.id == request.receipt_id).execution_options(populate_existing=True))
    ensure_owned(receipt, job.workspace_id, "ExternalCallReceipt")
    return job, request, receipt


def _result(db, request, outcome):
    if not (outcome.result_url or outcome.file_reference):
        return None
    return add_generation_result(db, request.shot_id, {
        "workspace_id": request.workspace_id,
        "prompt_id": request.prompt_id,
        "generation_request_id": request.id,
        "result_url": outcome.result_url,
        "file_reference": outcome.file_reference,
        "note": "Created by durable execution worker",
        "status": "candidate",
        "raw": {"providerResponse": outcome.response},
    }, commit=False)


def _provider_unknown(db, job, request, receipt, error, attempt_id=None):
    execution.mark_unknown(db, receipt.id, request.workspace_id, attempt_id=attempt_id,
        error=str(error), commit=False)
    execution.transition_generation_request(db, request.id, request.workspace_id, "unknown",
        error=str(error), commit=False)
    log_activity(db, "provider_unknown", "GenerationRequest", request.id,
        {"jobId": job.id, "error": str(error)}, workspace_id=request.workspace_id)
    fail_job(db, job.id, job.lease_owner, str(error), commit=False)
    db.commit()


def _submit(db, job, request, receipt, provider):
    attempt_holder = {"id": None}

    def on_dispatch():
        # This commit is the uncertainty boundary. If the process dies after it,
        # recovery must assume the provider might have received the request.
        attempt = execution.start_attempt(db, receipt.id, request.workspace_id, commit=False)
        execution.transition_generation_request(db, request.id, request.workspace_id, "submitting", commit=False)
        job.payload = {**(job.payload or {}), "dispatch_started": True, "attempt_id": attempt.id}
        log_activity(db, "generation_dispatched", "GenerationRequest", request.id,
            {"jobId": job.id, "attemptId": attempt.id}, workspace_id=request.workspace_id)
        db.commit()
        attempt_holder["id"] = attempt.id

    outcome = provider.submit(request, on_dispatch=on_dispatch, technical_attempt=job.attempt_count)
    job, request, receipt = _load(db, job.id, job.lease_owner)
    attempt_id = attempt_holder["id"] or (job.payload or {}).get("attempt_id")
    if outcome.status == "succeeded":
        execution.mark_completed(db, receipt.id, request.workspace_id, attempt_id=attempt_id,
            provider_request_id=outcome.provider_job_id, response_payload=outcome.response,
            usage=outcome.usage, cost=outcome.cost, currency=outcome.currency, commit=False)
        execution.transition_generation_request(db, request.id, request.workspace_id, "succeeded",
            provider_job_id=outcome.provider_job_id, commit=False)
        _result(db, request, outcome)
        succeed_job(db, job.id, job.lease_owner, commit=False)
        db.commit()
    elif outcome.status == "submitted":
        execution.mark_received(db, receipt.id, request.workspace_id, attempt_id=attempt_id,
            provider_request_id=outcome.provider_job_id, response_payload=outcome.response,
            usage=outcome.usage, cost=outcome.cost, currency=outcome.currency, commit=False)
        execution.transition_generation_request(db, request.id, request.workspace_id, "submitted",
            provider_job_id=outcome.provider_job_id, commit=False)
        delay = provider.poll_interval_seconds(request)
        job.payload = {**(job.payload or {}), "next_poll_sequence": 1}
        enqueue_poll(db, request, 1, available_at=utcnow() + timedelta(seconds=delay), delay_seconds=delay)
        succeed_job(db, job.id, job.lease_owner, commit=False)
        db.commit()
    elif outcome.status == "failed":
        execution.mark_failed(db, receipt.id, request.workspace_id, attempt_id=attempt_id,
            provider_request_id=outcome.provider_job_id, error=outcome.error, response_payload=outcome.response,
            commit=False)
        execution.transition_generation_request(db, request.id, request.workspace_id, "failed",
            error=outcome.error, commit=False)
        fail_job(db, job.id, job.lease_owner, outcome.error, commit=False)
        db.commit()
    else:
        _provider_unknown(db, job, request, receipt, outcome.error or "Unknown submit outcome", attempt_id)


def _poll(db, job, request, receipt, provider):
    if request.status == "submitted":
        execution.transition_generation_request(db, request.id, request.workspace_id, "polling",
            provider_job_id=request.provider_job_id, commit=False)
        db.flush()
    sequence = int((job.payload or {}).get("poll_sequence", 1))
    outcome = provider.poll(request, poll_sequence=sequence)
    job, request, receipt = _load(db, job.id, job.lease_owner)
    if outcome.status == "pending":
        delay = provider.poll_interval_seconds(request)
        enqueue_poll(db, request, sequence + 1, available_at=utcnow() + timedelta(seconds=delay), delay_seconds=delay)
        request.last_polled_at = utcnow()
        succeed_job(db, job.id, job.lease_owner, commit=False)
        db.commit()
    elif outcome.status == "succeeded":
        execution.mark_completed(db, receipt.id, request.workspace_id,
            provider_request_id=outcome.provider_job_id, response_payload=outcome.response,
            usage=outcome.usage, cost=outcome.cost, currency=outcome.currency, commit=False)
        execution.transition_generation_request(db, request.id, request.workspace_id, "succeeded",
            provider_job_id=outcome.provider_job_id, commit=False)
        _result(db, request, outcome)
        succeed_job(db, job.id, job.lease_owner, commit=False)
        db.commit()
    elif outcome.status == "failed":
        execution.mark_failed(db, receipt.id, request.workspace_id, provider_request_id=outcome.provider_job_id,
            error=outcome.error, response_payload=outcome.response, commit=False)
        execution.transition_generation_request(db, request.id, request.workspace_id, "failed",
            error=outcome.error, commit=False)
        fail_job(db, job.id, job.lease_owner, outcome.error, commit=False)
        db.commit()
    elif outcome.status == "cancelled":
        execution.transition_generation_request(db, request.id, request.workspace_id, "cancelled",
            provider_cancelled=True, commit=False)
        succeed_job(db, job.id, job.lease_owner, commit=False)
        db.commit()
    else:
        _provider_unknown(db, job, request, receipt, outcome.error or "Unknown polling outcome")


def _cancel(db, job, request, receipt, provider):
    job.payload = {**(job.payload or {}), "dispatch_started": True}
    db.commit()
    outcome = provider.cancel(request)
    job, request, receipt = _load(db, job.id, job.lease_owner)
    if outcome.status == "cancelled":
        execution.transition_generation_request(db, request.id, request.workspace_id, "cancelled",
            provider_cancelled=True, commit=False)
        for pending in db.scalars(select(ExecutionJob).where(
            ExecutionJob.generation_request_id == request.id,
            ExecutionJob.status == "queued",
            ExecutionJob.id != job.id,
        ).with_for_update()).all():
            pending.status = "cancelled"
            pending.completed_at = utcnow()
        succeed_job(db, job.id, job.lease_owner, commit=False)
        db.commit()
    elif outcome.status == "unsupported":
        fail_job(db, job.id, job.lease_owner, outcome.error, commit=False)
        db.commit()
    elif outcome.status == "failed":
        fail_job(db, job.id, job.lease_owner, outcome.error, commit=False)
        db.commit()
    else:
        _provider_unknown(db, job, request, receipt, outcome.error or "Unknown cancellation outcome")


def _reconcile(db, job, request, receipt, provider):
    outcome = provider.reconcile(request)
    job, request, receipt = _load(db, job.id, job.lease_owner)
    evidence = "Provider reconciliation lookup"
    if outcome.status == "succeeded":
        execution.mark_completed(db, receipt.id, request.workspace_id,
            provider_request_id=outcome.provider_job_id, response_payload=outcome.response,
            usage=outcome.usage, cost=outcome.cost, currency=outcome.currency,
            reconciliation=evidence, commit=False)
        execution.transition_generation_request(db, request.id, request.workspace_id, "succeeded",
            provider_job_id=outcome.provider_job_id, commit=False)
        _result(db, request, outcome)
        succeed_job(db, job.id, job.lease_owner, commit=False)
        db.commit()
    elif outcome.status == "failed":
        execution.mark_failed(db, receipt.id, request.workspace_id,
            provider_request_id=outcome.provider_job_id, error=outcome.error,
            reconciliation=evidence, commit=False)
        execution.transition_generation_request(db, request.id, request.workspace_id, "failed",
            error=outcome.error, commit=False)
        fail_job(db, job.id, job.lease_owner, outcome.error, commit=False)
        db.commit()
    elif outcome.status == "pending":
        execution.mark_received(db, receipt.id, request.workspace_id,
            provider_request_id=outcome.provider_job_id, response_payload=outcome.response,
            reconciliation=evidence, commit=False)
        execution.transition_generation_request(db, request.id, request.workspace_id, "submitted",
            provider_job_id=outcome.provider_job_id, commit=False)
        prior_sequences = [int((item.payload or {}).get("poll_sequence", 0)) for item in db.scalars(
            select(ExecutionJob).where(ExecutionJob.generation_request_id == request.id,
                                      ExecutionJob.job_type == POLL)).all()]
        sequence = max(prior_sequences, default=0) + 1
        delay = provider.poll_interval_seconds(request)
        enqueue_poll(db, request, sequence, available_at=utcnow() + timedelta(seconds=delay),
            delay_seconds=delay)
        succeed_job(db, job.id, job.lease_owner, commit=False)
        db.commit()
    else:
        fail_job(db, job.id, job.lease_owner,
            outcome.error or "Provider reconciliation remains unknown")


def process_job(db, job_id: str, worker_id: str):
    job, request, receipt = _load(db, job_id, worker_id)
    if request.status in {"succeeded", "cancelled"}:
        succeed_job(db, job.id, worker_id)
        return
    if (request.status == "unknown" or receipt.status == "unknown") and job.job_type != RECONCILE:
        fail_job(db, job.id, worker_id, "Unknown provider outcome requires reconciliation")
        return
    try:
        provider = get_video_provider(request.provider)
        if job.job_type == SUBMIT:
            _submit(db, job, request, receipt, provider)
        elif job.job_type == POLL:
            _poll(db, job, request, receipt, provider)
        elif job.job_type == CANCEL:
            _cancel(db, job, request, receipt, provider)
        elif job.job_type == RECONCILE:
            _reconcile(db, job, request, receipt, provider)
        else:
            fail_job(db, job.id, worker_id, "Unsupported execution job type")
    except ProviderError as exc:
        db.rollback()
        job, request, receipt = _load(db, job_id, worker_id)
        attempt_id = (job.payload or {}).get("attempt_id")
        if job.job_type == SUBMIT and exc.safe_to_resubmit and attempt_id:
            execution.mark_attempt_not_accepted(db, receipt.id, request.workspace_id,
                attempt_id, exc, commit=False)
            execution.transition_generation_request(db, request.id, request.workspace_id, "queued",
                error=str(exc), provider_not_accepted=True, commit=False)
            retry_job(db, job.id, worker_id, exc, delay_seconds=exc.retry_after, commit=False)
            db.commit()
        elif job.job_type in {POLL, RECONCILE, CANCEL} and exc.retryable:
            retry_job(db, job.id, worker_id, exc, delay_seconds=exc.retry_after)
        elif exc.dispatched or (job.payload or {}).get("dispatch_started"):
            _provider_unknown(db, job, request, receipt, exc, attempt_id)
        elif exc.retryable:
            retry_job(db, job.id, worker_id, exc, delay_seconds=exc.retry_after)
        else:
            execution.mark_pre_dispatch_failed(db, receipt.id, request.workspace_id, exc, commit=False)
            execution.transition_generation_request(db, request.id, request.workspace_id, "failed",
                error=str(exc), commit=False)
            fail_job(db, job.id, worker_id, exc, commit=False)
            db.commit()
    except Exception as exc:
        db.rollback()
        job, request, receipt = _load(db, job_id, worker_id)
        attempt_id = (job.payload or {}).get("attempt_id")
        if job.job_type in {SUBMIT, CANCEL} and (job.payload or {}).get("dispatch_started"):
            _provider_unknown(db, job, request, receipt, exc, attempt_id)
        else:
            retry_job(db, job.id, worker_id, exc)


def run_once(session_factory=SessionLocal, *, worker_id: str, lease_seconds: int = 30) -> bool:
    with session_factory() as db:
        job = claim_next_job(db, worker_id, lease_seconds=lease_seconds)
        if not job:
            return False
        job_id = job.id
    with LeaseHeartbeat(session_factory, job_id, worker_id, lease_seconds):
        with session_factory() as db:
            process_job(db, job_id, worker_id)
    return True


def main():
    parser = argparse.ArgumentParser(description="AI Content OS durable execution worker")
    parser.add_argument("--once", action="store_true", help="Process at most one available job")
    parser.add_argument("--recover-only", action="store_true", help="Recover expired leases and exit")
    parser.add_argument("--worker-id", default=f"{socket.gethostname()}-{uuid.uuid4().hex[:8]}")
    parser.add_argument("--lease-seconds", type=int, default=30)
    parser.add_argument("--idle-seconds", type=float, default=1.0)
    args = parser.parse_args()
    with SessionLocal() as db:
        recovered = recover_expired_leases(db)
    if args.recover_only:
        print(recovered)
        return
    if args.once:
        run_once(worker_id=args.worker_id, lease_seconds=args.lease_seconds)
        return
    while True:
        worked = run_once(worker_id=args.worker_id, lease_seconds=args.lease_seconds)
        if not worked:
            time.sleep(max(0.1, args.idle_seconds))


if __name__ == "__main__":
    main()
