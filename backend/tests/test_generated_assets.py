"""Durable generated-asset storage and queue integration tests."""
from __future__ import annotations

import hashlib
import json
from datetime import timedelta

import httpx
import pytest

from test_core_api import client
from test_queue import claim_process, create_request, enqueue, session, state
from app.config import Settings
from app.models import ExecutionJob, GeneratedAsset, VideoGenerationResult
from app.queue import claim_next_job, recover_expired_leases
from app.storage import LocalStorageAdapter, StorageError
from app.workflow import utcnow


PUBLIC_IP = ["93.184.216.34"]
VIDEO_BYTES = b"\x00\x00\x00\x18ftypmp42durable-video-test"


def adapter(tmp_path, handler=None, *, max_bytes=1024 * 1024):
    calls = {"count": 0, "authorization": []}

    def default_handler(request):
        calls["count"] += 1
        calls["authorization"].append(request.headers.get("Authorization"))
        return httpx.Response(200, headers={
            "Content-Type": "video/mp4",
            "Content-Length": str(len(VIDEO_BYTES)),
        }, content=VIDEO_BYTES)

    def wrapped(request):
        calls["count"] += 1
        calls["authorization"].append(request.headers.get("Authorization"))
        return handler(request)

    settings = Settings(
        database_url="sqlite://",
        generated_asset_storage_dir=str(tmp_path),
        generated_asset_max_bytes=max_bytes,
        generated_asset_download_timeout_seconds=2,
    )
    transport = httpx.MockTransport(wrapped if handler else default_handler)
    return LocalStorageAdapter(settings, httpx.Client(transport=transport), lambda _: PUBLIC_IP), calls


def test_local_adapter_streams_hashes_and_recovers_without_duplicate(tmp_path):
    storage, calls = adapter(tmp_path)
    key = "0123456789abcdef/asset_" + "a" * 32 + ".mp4"
    first = storage.store_from_url("https://cdn.example.com/temporary.mp4?signature=secret", key,
        metadata={"asset_id": "asset_1"})
    assert first.path.read_bytes() == VIDEO_BYTES
    assert first.file_size == len(VIDEO_BYTES)
    assert first.sha256 == hashlib.sha256(VIDEO_BYTES).hexdigest()
    assert first.mime_type == "video/mp4"
    assert calls == {"count": 1, "authorization": [None]}

    metadata = json.loads(first.path.with_suffix(".mp4.json").read_text(encoding="utf-8"))
    assert metadata["sha256"] == first.sha256
    assert "source_url" not in metadata
    assert "signature" not in json.dumps(metadata)

    # A crash after atomic rename but before database commit is recovered from
    # the stable file and cannot trigger a second network download or copy.
    first.path.with_suffix(".mp4.json").unlink()
    second = storage.store_from_url("https://cdn.example.com/temporary.mp4?signature=changed", key)
    assert second.sha256 == first.sha256
    assert calls["count"] == 1
    assert len(list(tmp_path.rglob("*.mp4"))) == 1


def test_local_adapter_blocks_unsafe_paths_urls_types_and_oversize(tmp_path):
    storage, _ = adapter(tmp_path)
    with pytest.raises(StorageError, match="storage key"):
        storage.path_for("../escape.mp4")
    with pytest.raises(StorageError, match="HTTPS"):
        storage.store_from_url("file:///etc/passwd", "0123456789abcdef/asset_" + "b" * 32 + ".mp4")

    wrong_type, _ = adapter(tmp_path / "wrong", lambda _: httpx.Response(
        200, headers={"Content-Type": "text/html"}, content=b"not video"))
    with pytest.raises(StorageError, match="Content-Type"):
        wrong_type.store_from_url("https://cdn.example.com/video", "0123456789abcdef/asset_" + "c" * 32 + ".mp4")
    assert not list((tmp_path / "wrong").rglob("*.part"))
    assert not list((tmp_path / "wrong").rglob("*.mp4"))

    oversized, _ = adapter(tmp_path / "large", lambda _: httpx.Response(
        200, headers={"Content-Type": "video/mp4", "Content-Length": "999"}, content=b"x"), max_bytes=10)
    with pytest.raises(StorageError, match="size limit"):
        oversized.store_from_url("https://cdn.example.com/video", "0123456789abcdef/asset_" + "d" * 32 + ".mp4")


def test_generation_result_enqueues_and_persists_one_asset(client, monkeypatch, tmp_path):
    shot, _, request = create_request(client, "asset_happy")
    storage, calls = adapter(tmp_path)
    monkeypatch.setattr("app.worker.get_storage_adapter", lambda: storage)
    monkeypatch.setattr("app.asset_routes.get_storage_adapter", lambda: storage)

    enqueue(client, request)
    claim_process("generation-worker")
    current = state(client, request)
    asset_jobs = [job for job in current["jobs"] if job["job_type"] == "asset.persist"]
    assert len(asset_jobs) == 1 and asset_jobs[0]["status"] == "queued"

    results = client.get(f"/api/video-shots/{shot['id']}/results").json()
    assert len(results) == 1 and results[0]["status"] == "candidate"
    result = results[0]
    assert result["generated_asset"]["status"] == "pending"
    assert result["generated_asset"]["source_url"] == result["result_url"]

    claim_process("asset-worker")
    stored = client.get(f"/api/video-results/{result['id']}/asset").json()
    assert stored["status"] == "stored"
    assert stored["file_size"] == len(VIDEO_BYTES)
    assert stored["sha256"] == hashlib.sha256(VIDEO_BYTES).hexdigest()
    assert stored["mime_type"] == "video/mp4"
    assert client.get(stored["durable_url"]).content == VIDEO_BYTES

    # Duplicate persistence returns the same asset and reuses the same job/file.
    retried = client.post(f"/api/video-results/{result['id']}/asset/retry").json()
    assert retried["id"] == stored["id"] and retried["status"] == "stored"
    assert calls["count"] == 1
    assert len(list(tmp_path.rglob("*.mp4"))) == 1
    latest = state(client, request)
    assert len([job for job in latest["jobs"] if job["job_type"] == "asset.persist"]) == 1
    assert client.get(f"/api/generated-assets/{stored['id']}", params={"workspace_id": "other"}).status_code == 409

    actions = {item["action"] for item in client.get("/api/activity-logs").json()}
    assert {"generated_asset_created", "generated_asset_stored"} <= actions


def test_asset_failure_keeps_candidate_and_can_retry_independently(client, monkeypatch, tmp_path):
    shot, _, request = create_request(client, "asset_retry")
    failing, _ = adapter(tmp_path, lambda _: httpx.Response(
        200, headers={"Content-Type": "text/plain"}, content=b"bad"))
    monkeypatch.setattr("app.worker.get_storage_adapter", lambda: failing)
    enqueue(client, request)
    claim_process("generation-worker")
    claim_process("asset-worker")

    result = client.get(f"/api/video-shots/{shot['id']}/results").json()[0]
    failed = client.get(f"/api/video-results/{result['id']}/asset").json()
    assert result["status"] == "candidate"
    assert failed["status"] == "failed"
    assert failed["last_error"]

    working, calls = adapter(tmp_path)
    monkeypatch.setattr("app.worker.get_storage_adapter", lambda: working)
    retried = client.post(f"/api/video-results/{result['id']}/asset/retry")
    assert retried.status_code == 200 and retried.json()["id"] == failed["id"]
    claim_process("asset-retry-worker")
    stored = client.get(f"/api/video-results/{result['id']}/asset").json()
    assert stored["status"] == "stored" and calls["count"] == 1
    assert client.get(f"/api/video-shots/{shot['id']}/results").json()[0]["status"] == "candidate"


def test_expired_asset_lease_requeues_and_manual_result_is_unchanged(client, monkeypatch, tmp_path):
    shot, prompt, request = create_request(client, "asset_recovery")
    storage, calls = adapter(tmp_path)
    monkeypatch.setattr("app.worker.get_storage_adapter", lambda: storage)
    enqueue(client, request)
    claim_process("generation-worker")

    with session() as db:
        job = claim_next_job(db, "crashed-worker", lease_seconds=30)
        assert job.job_type == "asset.persist"
        asset = db.get(GeneratedAsset, job.payload["asset_id"])
        # The binary reached its atomic final name, but the process died before
        # marking the database row stored.
        storage.store_from_url(asset.source_url, asset.storage_key)
        job.lease_expires_at = utcnow()
        db.commit()
    with session() as db:
        assert recover_expired_leases(db, now=utcnow())["requeued"] == 1
    claim_process("recovery-worker", now=utcnow() + timedelta(seconds=5))
    result = client.get(f"/api/video-shots/{shot['id']}/results").json()[0]
    assert result["generated_asset"]["status"] == "stored"
    assert calls["count"] == 1
    assert len(list(tmp_path.rglob("*.mp4"))) == 1

    manual = client.post(f"/api/video-shots/{shot['id']}/results", json={
        "prompt_id": prompt["id"],
        "result_url": "https://example.com/manual.mp4",
        "status": "candidate",
    })
    assert manual.status_code == 200
    assert manual.json()["generation_request_id"] is None
    assert manual.json()["generated_asset"] is None
    with session() as db:
        manual_result = db.get(VideoGenerationResult, manual.json()["id"])
        assert manual_result is not None
        assert not db.query(ExecutionJob).filter(ExecutionJob.subject_id == manual_result.id).count()
