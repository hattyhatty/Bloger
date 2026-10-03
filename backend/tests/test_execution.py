"""Execution core contracts; never invokes a provider."""
from test_core_api import client, create_video_plan_fixture
from app.execution import logical_key
from app.prompt_registry import PromptRegistry, template_from_content
import os
import pytest


def setup_prompt(client, suffix="execution", workspace="default"):
    content, plan = create_video_plan_fixture(client, suffix, workspace)
    assert client.put(f"/api/video-plans/{plan['id']}/script", json={"workspace_id": workspace,
        "hook": "Hook", "main_story_flow": "Facts first", "narration_dialogue": "Narration", "estimated_duration_seconds": 30}).status_code == 200
    response = client.post(f"/api/video-plans/{plan['id']}/storyboard/generate", json={"workspace_id": workspace,
        "recurring_character_description": "Creator", "clothing": "blue jacket",
        "shots": [{"scene_description": "Studio", "estimated_duration_seconds": 5}]})
    assert response.status_code == 200, response.text
    shot = response.json()["shots"][0]
    response = client.put(f"/api/video-shots/{shot['id']}/prompt", json={"workspace_id": workspace,
        "prompt_target": "Kling", "generic_video_prompt": "Creator in studio"})
    assert response.status_code == 200, response.text
    return content, plan, shot, response.json()


def create(client, prompt, **values):
    response = client.post("/api/execution/generation-requests", json={"prompt_id": prompt["id"], "provider": "Kling", "model": "v1", **values})
    assert response.status_code == 200, response.text
    return response.json()


def start(client, request):
    response = client.post(f"/api/execution/receipts/{request['receipt_id']}/attempts", json={})
    assert response.status_code == 200, response.text
    return response.json()


def outcome(client, request, status, **values):
    return client.patch(f"/api/execution/receipts/{request['receipt_id']}/outcome", json={"status": status, **values})


def transition(client, request, status, **values):
    return client.patch(f"/api/execution/generation-requests/{request['id']}/status", json={"status": status, **values})


def test_stable_key_and_template_version():
    values = dict(workspace_id="w", service="video", purpose="generate", subject_type="Content", subject_id="c",
        input_revision="1", input_hash="a"*64, provider="Kling", model="v1", prompt_key="video.generate",
        prompt_version="b"*64, prompt_hash="b"*64, artifact_revision=1, config_hash="c"*64)
    assert logical_key(**values) == logical_key(**dict(reversed(list(values.items()))))
    for field in ("workspace_id", "input_hash", "input_revision", "provider", "model", "prompt_version", "prompt_hash", "artifact_revision", "config_hash"):
        changed = {**values, field: 2 if field == "artifact_revision" else "changed"}
        assert logical_key(**changed) != logical_key(**values)
    assert template_from_content("k", "one").version != template_from_content("k", "two").version
    assert PromptRegistry.get("video.generate").version == PromptRegistry.get("video.generate").hash


def test_duplicate_and_changed_inputs(client, monkeypatch):
    _, _, shot, prompt = setup_prompt(client)
    request = create(client, prompt, generation_config={"seed": 1, "duration": 5})
    assert create(client, prompt, generation_config={"duration": 5, "seed": 1})["id"] == request["id"]
    assert len(client.get("/api/execution/receipts").json()) == 1
    for values in ({"provider": "Veo"}, {"model": "v2"}, {"generation_config": {"seed": 2}}):
        assert create(client, prompt, **values)["logical_key"] != request["logical_key"]
    revised = client.put(f"/api/video-shots/{shot['id']}/prompt", json={"prompt_target": "Kling", "generic_video_prompt": "Changed"}).json()
    newer = create(client, revised)
    assert newer["prompt_revision"] == prompt["revision"] + 1
    assert newer["logical_key"] != request["logical_key"]
    old_snapshot = client.get(f"/api/execution/generation-requests/{request['id']}").json()["input_snapshot"]
    assert old_snapshot["prompt"]["genericVideoPrompt"] == "Creator in studio"
    monkeypatch.setattr(PromptRegistry, "get", classmethod(lambda cls, key: template_from_content(key, "new template")))
    assert create(client, revised)["logical_key"] != newer["logical_key"]


def test_attempt_history_and_unknown(client):
    _, _, _, prompt = setup_prompt(client)
    request = create(client, prompt)
    first = start(client, request)
    assert client.post(f"/api/execution/receipts/{request['receipt_id']}/attempts", json={}).status_code == 409
    assert outcome(client, request, "failed", attempt_id=first["id"], error="Invalid provider parameter").status_code == 200
    second = start(client, request)
    assert second["attempt_number"] == 2
    # Late callback from first attempt must not overwrite the second attempt.
    assert outcome(client, request, "completed", attempt_id=first["id"]).status_code == 409
    assert outcome(client, request, "unknown", attempt_id=second["id"], error="Timeout after dispatch").status_code == 200
    assert client.post(f"/api/execution/receipts/{request['receipt_id']}/attempts", json={}).status_code == 409
    assert outcome(client, request, "received").status_code == 409
    assert outcome(client, request, "received", provider_request_id="provider-1", reconciliation="Provider lookup confirmed acceptance").status_code == 200
    assert outcome(client, request, "completed", response_payload={"url": "https://example.com/result"}).status_code == 200
    history = client.get(f"/api/execution/receipts/{request['receipt_id']}").json()
    assert [item["status"] for item in history["attempts"]] == ["failed", "unknown"]
    assert history["attempts"][0]["error"] == "Invalid provider parameter"
    assert all(item["finished_at"] and item["latency_ms"] >= 0 for item in history["attempts"])


def test_transitions_and_result_snapshot(client):
    _, _, shot, prompt = setup_prompt(client)
    request = create(client, prompt)
    assert transition(client, request, "succeeded").status_code == 409
    assert transition(client, request, "submitting").status_code == 409
    assert transition(client, request, "queued").status_code == 200
    attempt = start(client, request)
    assert transition(client, request, "cancelled").status_code == 409
    assert transition(client, request, "submitting").status_code == 200
    assert outcome(client, request, "received", attempt_id=attempt["id"], provider_request_id="job-1").status_code == 200
    assert transition(client, request, "submitted").status_code == 409
    assert transition(client, request, "submitted", provider_job_id="job-1").status_code == 200
    assert transition(client, request, "polling").status_code == 200
    assert outcome(client, request, "completed", response_payload={"url": "https://example.com/video"}).status_code == 200
    assert transition(client, request, "succeeded").status_code == 200
    assert transition(client, request, "queued").status_code == 409
    client.put(f"/api/video-shots/{shot['id']}/prompt", json={"prompt_target": "Kling", "generic_video_prompt": "Later edit"})
    payload = {"prompt_id": prompt["id"], "generation_request_id": request["id"], "result_url": "https://example.com/video", "status": "selected"}
    response = client.post(f"/api/video-shots/{shot['id']}/results", json=payload)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["prompt_snapshot"]["genericVideoPrompt"] == "Creator in studio"
    assert result["prompt_revision"] == prompt["revision"]
    assert result["provider"] == "Kling"
    assert client.post(f"/api/video-shots/{shot['id']}/results", json=payload).json()["id"] == result["id"]
    assert client.delete(f"/api/video-shots/{shot['id']}").status_code == 409
    # Existing manual mode remains valid and retains the selected-result invariant.
    manual = client.post(f"/api/video-shots/{shot['id']}/results", json={"prompt_id": prompt["id"], "result_url": "https://example.com/manual", "status": "selected"})
    assert manual.status_code == 200 and manual.json()["generation_request_id"] is None
    results = client.get(f"/api/video-shots/{shot['id']}/results").json()
    assert sum(item["status"] == "selected" for item in results) == 1


def test_unknown_request_no_retry_and_workspace_boundary(client):
    _, _, shot, prompt = setup_prompt(client)
    request = create(client, prompt)
    attempt = start(client, request)
    assert transition(client, request, "submitting").status_code == 200
    assert outcome(client, request, "unknown", attempt_id=attempt["id"], error="Process crash").status_code == 200
    assert transition(client, request, "unknown").status_code == 200
    assert transition(client, request, "queued").status_code == 409
    assert transition(client, request, "submitting").status_code == 409
    assert client.post("/api/execution/generation-requests", json={"workspace_id": "other", "prompt_id": prompt["id"], "provider": "Kling"}).status_code == 409
    assert client.get(f"/api/execution/receipts/{request['receipt_id']}", params={"workspace_id": "other"}).status_code == 409
    assert client.patch(f"/api/execution/generation-requests/{request['id']}/status", json={"workspace_id": "other", "status": "cancelled"}).status_code == 409
    assert client.get("/api/execution/generation-requests", params={"workspace_id": "other"}).json() == []
    assert client.delete(f"/api/video-shots/{shot['id']}").status_code == 409
    assert client.post("/api/execution/generation-requests", json={"prompt_id": prompt["id"], "provider": "Kling", "generation_config": {"api_key": "not-a-real-key"}}).status_code == 409


def test_generic_receipt_and_activity(client):
    content, _, _, _ = setup_prompt(client)
    payload = {"service": "research", "purpose": "analyze", "provider": "mock", "model": "text",
        "subject_type": "Content", "subject_id": content["id"], "input_revision": "1", "input_hash": "a"*64, "prompt_key": "research.analyze"}
    first = client.post("/api/execution/receipts", json=payload)
    assert first.status_code == 200, first.text
    assert client.post("/api/execution/receipts", json=payload).json()["id"] == first.json()["id"]
    assert client.post("/api/execution/receipts", json={**payload, "workspace_id": "other"}).status_code == 409
    logs = client.get("/api/activity-logs").json()
    actions = {item["action"] for item in logs}
    assert {"external_receipt_created", "external_receipt_reused"} <= actions


def test_failed_request_retry_and_cancel(client):
    _, _, shot, prompt = setup_prompt(client)
    request = create(client, prompt)
    assert client.post(f"/api/video-shots/{shot['id']}/results", json={"prompt_id": prompt["id"],
        "generation_request_id": request["id"], "result_url": "https://example.com/premature"}).status_code == 409
    first = start(client, request)
    assert transition(client, request, "submitting").status_code == 200
    assert outcome(client, request, "failed", attempt_id=first["id"], error="Rejected").status_code == 200
    assert transition(client, request, "failed").status_code == 200
    assert transition(client, request, "queued").status_code == 200
    second = start(client, request)
    assert transition(client, request, "submitting").status_code == 200
    assert outcome(client, request, "completed", attempt_id=second["id"], response_payload={"asset": "result"}, usage={"units": 1}, cost="0.10", currency="USD").status_code == 200
    assert transition(client, request, "succeeded").status_code == 200
    history = client.get(f"/api/execution/receipts/{request['receipt_id']}").json()
    assert [item["status"] for item in history["attempts"]] == ["failed", "completed"]
    assert history["receipt"]["cost"] == "0.10"
    cancelled = create(client, prompt, generation_config={"seed": 42})
    assert transition(client, cancelled, "cancelled").status_code == 200
    assert transition(client, cancelled, "queued").status_code == 409
    assert client.post(f"/api/execution/receipts/{cancelled['receipt_id']}/attempts", json={}).status_code == 409


def test_retry_after_accepted_provider_failure(client):
    _, _, _, prompt = setup_prompt(client)
    request = create(client, prompt)
    first = start(client, request)
    assert transition(client, request, "submitting").status_code == 200
    assert outcome(client, request, "received", attempt_id=first["id"], provider_request_id="job-old").status_code == 200
    assert transition(client, request, "submitted", provider_job_id="job-old").status_code == 200
    assert outcome(client, request, "failed", error="Provider confirmed terminal rejection").status_code == 200
    assert transition(client, request, "failed").status_code == 200
    assert transition(client, request, "queued").json()["provider_job_id"] == ""
    second = start(client, request)
    assert transition(client, request, "submitting").status_code == 200
    assert outcome(client, request, "received", attempt_id=second["id"], provider_request_id="job-new").status_code == 200
    assert outcome(client, request, "completed", attempt_id=first["id"]).status_code == 409
    assert transition(client, request, "submitted", provider_job_id="job-new").status_code == 200
    history = client.get(f"/api/execution/receipts/{request['receipt_id']}").json()
    assert [row["provider_request_id"] for row in history["attempts"]] == ["job-old", "job-new"]


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="Requires PostgreSQL row locks")
def test_postgres_concurrent_duplicate_creation_and_attempt(client):
    from concurrent.futures import ThreadPoolExecutor
    from app.database import get_db
    from app.main import app
    from app.execution import create_generation_request, start_attempt
    from app.workflow import WorkflowConflict
    _, _, _, prompt = setup_prompt(client)
    factory = app.dependency_overrides[get_db]

    def create_in_session(_):
        generator = factory()
        db = next(generator)
        try:
            return create_generation_request(db, {"workspace_id": "default", "prompt_id": prompt["id"], "provider": "Kling", "model": "v1"}).id
        finally:
            generator.close()

    with ThreadPoolExecutor(max_workers=4) as pool:
        ids = list(pool.map(create_in_session, range(4)))
    assert len(set(ids)) == 1
    request = client.get(f"/api/execution/generation-requests/{ids[0]}").json()
    assert len(client.get("/api/execution/receipts").json()) == 1

    def start_in_session(_):
        generator = factory()
        db = next(generator)
        try:
            return start_attempt(db, request["receipt_id"], "default").id
        except WorkflowConflict:
            db.rollback()
            return None
        finally:
            generator.close()

    with ThreadPoolExecutor(max_workers=4) as pool:
        attempts = list(pool.map(start_in_session, range(4)))
    assert sum(item is not None for item in attempts) == 1
    assert len(client.get(f"/api/execution/receipts/{request['receipt_id']}").json()["attempts"]) == 1
