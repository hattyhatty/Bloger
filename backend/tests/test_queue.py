"""Durable worker lifecycle tests. PostgreSQL-only tests prove queue concurrency."""
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import os

import pytest
from sqlalchemy import select

from test_core_api import client
from test_execution import setup_prompt
from app import execution
from app.database import get_db
from app.main import app
from app.models import ExecutionJob, GenerationRequest
from app.providers import FakeVideoProvider
from app.queue import claim_next_job, heartbeat, recover_expired_leases
from app.worker import process_job
from app.workflow import WorkflowConflict, utcnow


@contextmanager
def session():
    generator = app.dependency_overrides[get_db]()
    db = next(generator)
    try:
        yield db
    finally:
        generator.close()


def create_request(client, suffix, mode="immediate_success", **config):
    _, _, shot, prompt = setup_prompt(client, suffix)
    payload = {"prompt_id": prompt["id"], "provider": "Fake", "model": "fake-v1",
        "generation_config": {"fake_mode": mode, **config}}
    response = client.post("/api/execution/generation-requests", json=payload)
    assert response.status_code == 200, response.text
    return shot, prompt, response.json()


def enqueue(client, request, **values):
    response = client.post(f"/api/execution/generation-requests/{request['id']}/enqueue", json=values)
    assert response.status_code == 200, response.text
    return response.json()


def claim_process(worker="test-worker", now=None):
    with session() as db:
        job = claim_next_job(db, worker, lease_seconds=30, now=now)
        assert job is not None
        process_job(db, job.id, worker)
        return job.id


def state(client, request):
    response = client.get(f"/api/execution/generation-requests/{request['id']}/execution-state")
    assert response.status_code == 200, response.text
    return response.json()


def test_transactional_enqueue_duplicate_and_cancel(client, monkeypatch):
    _, _, request = create_request(client, "queue_atomic")
    job = enqueue(client, request)
    assert state(client, request)["request"]["status"] == "queued"
    duplicate = enqueue(client, request)
    assert duplicate["id"] == job["id"]
    assert len(state(client, request)["jobs"]) == 1
    cancelled = client.post(f"/api/execution/generation-requests/{request['id']}/cancel", json={})
    assert cancelled.status_code == 200
    latest = state(client, request)
    assert latest["request"]["status"] == "cancelled"
    assert latest["jobs"][0]["status"] == "cancelled"
    with session() as db:
        assert claim_next_job(db, "nobody") is None

    # A simulated commit crash rolls back both request status and job insert.
    _, _, request2 = create_request(client, "queue_atomic_crash")
    with session() as db:
        original = db.commit
        monkeypatch.setattr(db, "commit", lambda: (_ for _ in ()).throw(RuntimeError("simulated crash")))
        with pytest.raises(RuntimeError):
            from app.queue import enqueue_generation_request
            enqueue_generation_request(db, request2["id"])
        db.rollback()
        monkeypatch.setattr(db, "commit", original)
    assert state(client, request2)["request"]["status"] == "created"
    assert state(client, request2)["jobs"] == []


def test_fake_immediate_success_creates_candidate(client):
    shot, _, request = create_request(client, "queue_immediate")
    enqueue(client, request)
    claim_process()
    current = state(client, request)
    assert current["request"]["status"] == "succeeded"
    assert current["receipt"]["status"] == "completed"
    assert current["jobs"][0]["status"] == "succeeded"
    results = client.get(f"/api/video-shots/{shot['id']}/results").json()
    assert len(results) == 1
    assert results[0]["status"] == "candidate"
    assert results[0]["generation_request_id"] == request["id"]


def test_fake_async_poll_jobs_are_short_and_idempotent(client):
    shot, _, request = create_request(client, "queue_async", "async_success",
        ready_after_polls=2, poll_interval_seconds=0)
    enqueue(client, request)
    claim_process("submit")
    current = state(client, request)
    assert current["request"]["status"] == "submitted"
    assert sorted(job["job_type"] for job in current["jobs"]) == ["generation.poll", "generation.submit"]
    claim_process("poll-1")
    current = state(client, request)
    assert current["request"]["status"] == "polling"
    assert len([job for job in current["jobs"] if job["job_type"] == "generation.poll"]) == 2
    claim_process("poll-2")
    current = state(client, request)
    assert current["request"]["status"] == "succeeded"
    assert all(job["status"] == "succeeded" for job in current["jobs"])
    assert client.get(f"/api/video-shots/{shot['id']}/results").json()[0]["status"] == "candidate"
    actions = {row["action"] for row in client.get("/api/activity-logs").json()}
    assert {"job_enqueued", "job_claimed", "generation_dispatched", "polling_scheduled", "job_succeeded"} <= actions


def test_definitive_failure_and_transport_unknown(client):
    _, _, failed = create_request(client, "queue_failure", "definitive_failure")
    failed_job = enqueue(client, failed)
    claim_process("failure")
    current = state(client, failed)
    assert current["request"]["status"] == "failed"
    assert current["receipt"]["status"] == "failed"
    assert current["jobs"][0]["status"] == "failed"
    retry = client.post(f"/api/execution/jobs/{failed_job['id']}/retry", json={})
    assert retry.status_code == 200 and retry.json()["status"] == "queued"
    assert client.post(f"/api/execution/generation-requests/{failed['id']}/cancel", json={}).status_code == 200

    _, _, unknown = create_request(client, "queue_unknown", "transport_unknown")
    unknown_job = enqueue(client, unknown)
    claim_process("unknown")
    current = state(client, unknown)
    assert current["request"]["status"] == "unknown"
    assert current["receipt"]["status"] == "unknown"
    assert current["jobs"][0]["status"] == "failed"
    assert client.post(f"/api/execution/jobs/{unknown_job['id']}/retry", json={}).status_code == 409
    assert client.post(f"/api/execution/generation-requests/{unknown['id']}/enqueue", json={}).status_code == 409


def test_retry_backoff_and_max_attempts_dead(client):
    _, _, request = create_request(client, "queue_retry", "retryable_error",
        transient_failures=1)
    enqueue(client, request, max_attempts=3)
    claim_process("retry-1")
    current = state(client, request)
    job = current["jobs"][0]
    assert job["status"] == "queued" and job["attempt_count"] == 1
    assert job["available_at"] is not None and job["heartbeat_at"] is None
    claim_process("retry-2", utcnow() + timedelta(seconds=10))
    assert state(client, request)["request"]["status"] == "succeeded"

    _, _, doomed = create_request(client, "queue_dead", "retryable_error",
        transient_failures=9)
    enqueue(client, doomed, max_attempts=2)
    claim_process("dead-1")
    claim_process("dead-2", utcnow() + timedelta(seconds=10))
    current = state(client, doomed)
    assert current["request"]["status"] == "queued"
    assert current["jobs"][0]["status"] == "dead"


def test_lease_heartbeat_and_recovery_before_dispatch(client):
    _, _, request = create_request(client, "queue_recover_safe")
    enqueue(client, request)
    with session() as db:
        job = claim_next_job(db, "owner", lease_seconds=30)
        with pytest.raises(WorkflowConflict):
            heartbeat(db, job.id, "other", lease_seconds=30)
        renewed = heartbeat(db, job.id, "owner", lease_seconds=60)
        assert renewed.lease_owner == "owner"
        renewed.lease_expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
    with session() as db:
        summary = recover_expired_leases(db)
        assert summary["requeued"] == 1
    current = state(client, request)
    assert current["request"]["status"] == "queued"
    assert current["jobs"][0]["status"] == "queued"


def test_recovery_after_dispatch_marks_unknown(client):
    _, _, request = create_request(client, "queue_recover_unknown")
    enqueue(client, request)
    with session() as db:
        job = claim_next_job(db, "crashed", lease_seconds=30)
        attempt = execution.start_attempt(db, request["receipt_id"], "default", commit=False)
        execution.transition_generation_request(db, request["id"], "default", "submitting", commit=False)
        job = db.get(ExecutionJob, job.id)
        job.payload = {"dispatch_started": True, "attempt_id": attempt.id}
        job.lease_expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
    with session() as db:
        first = recover_expired_leases(db)
        second = recover_expired_leases(db)
        assert first["unknown"] == 1
        assert second == {"requeued": 0, "unknown": 0, "completed": 0, "dead": 0}
    current = state(client, request)
    assert current["request"]["status"] == "unknown"
    assert current["receipt"]["status"] == "unknown"
    assert current["attempts"][0]["status"] == "unknown"
    assert current["jobs"][0]["status"] == "failed"


def test_submitted_cancellation_boundary(client):
    _, _, request = create_request(client, "queue_cancel", "async_success",
        poll_interval_seconds=120, cancel_supported=True)
    enqueue(client, request)
    claim_process("submit-cancel")
    response = client.post(f"/api/execution/generation-requests/{request['id']}/cancel", json={})
    assert response.status_code == 200 and response.json()["job"]["job_type"] == "generation.cancel"
    claim_process("cancel-worker")
    current = state(client, request)
    assert current["request"]["status"] == "cancelled"
    assert [job for job in current["jobs"] if job["job_type"] == "generation.poll"][0]["status"] == "cancelled"


def test_workspace_boundaries_and_fake_reconcile(client):
    _, _, request = create_request(client, "queue_workspace", "reconcile_success")
    job = enqueue(client, request)
    assert client.get(f"/api/execution/generation-requests/{request['id']}/execution-state",
        params={"workspace_id": "other"}).status_code == 409
    assert client.post(f"/api/execution/jobs/{job['id']}/retry", json={"workspace_id": "other"}).status_code == 409
    with session() as db:
        model = db.get(GenerationRequest, request["id"])
        success = FakeVideoProvider().reconcile(model)
        model.generation_config = {"fake_mode": "reconcile_failure"}
        failure = FakeVideoProvider().reconcile(model)
        assert success.status == "succeeded" and failure.status == "failed"


def test_unknown_reconciliation_job_can_confirm_success(client):
    shot, _, request = create_request(client, "queue_reconcile", "transport_unknown",
        reconcile_outcome="reconcile_success")
    enqueue(client, request)
    claim_process("unknown-submit")
    assert state(client, request)["request"]["status"] == "unknown"
    response = client.post(f"/api/execution/generation-requests/{request['id']}/reconcile", json={})
    assert response.status_code == 200, response.text
    claim_process("reconciler")
    current = state(client, request)
    assert current["request"]["status"] == "succeeded"
    assert current["receipt"]["status"] == "completed"
    assert client.get(f"/api/video-shots/{shot['id']}/results").json()[0]["status"] == "candidate"


def test_unknown_reconciliation_failure_is_confirmed(client):
    _, _, request = create_request(client, "queue_reconcile_failure", "transport_unknown",
        reconcile_outcome="reconcile_failure")
    enqueue(client, request)
    claim_process("unknown-submit-failure")
    reconcile = client.post(f"/api/execution/generation-requests/{request['id']}/reconcile", json={})
    assert reconcile.status_code == 200
    claim_process("reconciler-failure")
    current = state(client, request)
    assert current["request"]["status"] == "failed"
    assert current["receipt"]["status"] == "failed"
    assert [job for job in current["jobs"] if job["job_type"] == "generation.reconcile"][0]["status"] == "failed"


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="Requires PostgreSQL SKIP LOCKED")
def test_postgres_two_workers_claim_once(client):
    _, _, request = create_request(client, "queue_concurrent")
    enqueue(client, request)

    def claim(worker):
        with session() as db:
            job = claim_next_job(db, worker)
            return job.id if job else None

    with ThreadPoolExecutor(max_workers=2) as pool:
        claims = list(pool.map(claim, ("worker-a", "worker-b")))
    assert sum(item is not None for item in claims) == 1
    current = state(client, request)
    assert current["jobs"][0]["attempt_count"] == 1
