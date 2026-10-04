"""Runway contract tests use MockTransport and never spend provider credits."""
from types import SimpleNamespace

import httpx
import pytest

from test_core_api import client
from app.config import Settings
from app.providers import ProviderPollingRetryable, ProviderRateLimited, ProviderUnavailable
from app.runway_provider import RunwayVideoProvider


def settings(secret="test-secret"):
    return Settings(database_url="sqlite://", runwayml_api_secret=secret)


def request(**changes):
    data = {
        "model": "gen4.5",
        "provider_job_id": "task-123",
        "generation_config": {"duration": 5, "ratio": "1280:720"},
        "input_snapshot": {
            "shot": {"estimatedDurationSeconds": 5},
            "video_plan": {"aspect_ratio": "16:9"},
            "prompt": {"genericVideoPrompt": "A creator walks into a studio",
                       "continuityNotes": "Keep the blue jacket consistent",
                       "negativeInstructions": "No distorted hands"},
            "reference_assets": [],
        },
    }
    data.update(changes)
    return SimpleNamespace(**data)


def provider(handler, secret="test-secret"):
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return RunwayVideoProvider(settings(secret), client)


def test_submit_maps_immutable_snapshot_and_omits_unsupported_negative_prompt():
    captured = {}

    def handler(http_request):
        captured["request"] = http_request
        import json
        captured["body"] = json.loads(http_request.content)
        return httpx.Response(200, json={"id": "task-abc"})

    dispatched = []
    outcome = provider(handler).submit(request(), on_dispatch=lambda: dispatched.append(True))
    assert dispatched == [True]
    assert outcome.status == "submitted" and outcome.provider_job_id == "task-abc"
    assert captured["request"].url.path == "/v1/text_to_video"
    assert captured["request"].headers["x-runway-version"] == "2024-11-06"
    assert captured["body"] == {
        "model": "gen4.5",
        "promptText": "A creator walks into a studio\n\nKeep the blue jacket consistent",
        "ratio": "1280:720",
        "duration": 5,
    }
    assert "negative" not in str(captured["body"]).lower()


def test_reference_mapping_and_local_reference_rejection():
    seen = {}

    def handler(http_request):
        import json
        seen.update(json.loads(http_request.content))
        return httpx.Response(200, json={"id": "task-image"})

    snapshot = request().input_snapshot
    snapshot["reference_assets"] = [{"id": "asset-1", "status": "active",
        "reference_url": "https://cdn.example.com/character.png", "file_reference": ""}]
    outcome = provider(handler).submit(request(input_snapshot=snapshot), on_dispatch=lambda: None)
    assert outcome.provider_job_id == "task-image"
    assert seen["promptImage"] == "https://cdn.example.com/character.png"

    def image_handler(http_request):
        assert http_request.url.path == "/v1/image_to_video"
        return httpx.Response(200, json={"id": "task-image"})

    provider(image_handler).submit(request(input_snapshot=snapshot), on_dispatch=lambda: None)

    snapshot["reference_assets"][0] = {"id": "asset-1", "status": "active",
        "reference_url": "", "file_reference": "C:/private/character.png"}
    with pytest.raises(ProviderUnavailable, match="public HTTPS"):
        provider(handler).build_payload(request(input_snapshot=snapshot))


def test_missing_credential_and_validation_happen_before_dispatch():
    dispatched = []
    adapter = provider(lambda _: httpx.Response(500), secret="")
    with pytest.raises(ProviderUnavailable, match="credential") as error:
        adapter.submit(request(), on_dispatch=lambda: dispatched.append(True))
    assert not error.value.dispatched
    assert dispatched == []

    invalid = request(generation_config={"duration": 11, "ratio": "1280:720"})
    with pytest.raises(ProviderUnavailable, match="between 2 and 10"):
        provider(lambda _: httpx.Response(500)).submit(invalid, on_dispatch=lambda: dispatched.append(True))
    assert dispatched == []


def test_submit_rate_limit_and_timeout_have_explicit_certainty():
    limited = provider(lambda _: httpx.Response(429, headers={"Retry-After": "17"}, json={"error": "quota"}))
    with pytest.raises(ProviderRateLimited) as error:
        limited.submit(request(), on_dispatch=lambda: None)
    assert error.value.dispatched and error.value.safe_to_resubmit
    assert error.value.retry_after == 17

    def timeout(http_request):
        raise httpx.ReadTimeout("late timeout", request=http_request)

    with pytest.raises(ProviderUnavailable) as error:
        provider(timeout).submit(request(), on_dispatch=lambda: None)
    assert error.value.dispatched and not error.value.retryable


def test_auth_failure_is_definitive_and_reconcile_without_id_is_manual():
    outcome = provider(lambda _: httpx.Response(401, json={"error": "invalid key"})).submit(
        request(), on_dispatch=lambda: None)
    assert outcome.status == "failed"
    assert "401" in outcome.error
    unresolved = provider(lambda _: httpx.Response(500)).reconcile(request(provider_job_id=""))
    assert unresolved.status == "unknown"
    assert "manual_reconciliation_required" in unresolved.error


@pytest.mark.parametrize("status,expected", [
    ("PENDING", "pending"), ("RUNNING", "pending"), ("THROTTLED", "pending"),
    ("FAILED", "failed"), ("CANCELED", "cancelled"),
])
def test_poll_status_mapping(status, expected):
    outcome = provider(lambda _: httpx.Response(200, json={"status": status,
        "failure": "safety" if status == "FAILED" else None})).poll(request(), poll_sequence=1)
    assert outcome.status == expected


def test_poll_success_retry_and_reconcile():
    success = provider(lambda _: httpx.Response(200, json={"status": "SUCCEEDED",
        "output": ["https://cdn.example.com/result.mp4"]}))
    outcome = success.poll(request(), poll_sequence=3)
    assert outcome.status == "succeeded"
    assert outcome.result_url.endswith("result.mp4")
    assert success.reconcile(request()).status == "succeeded"

    retry = provider(lambda _: httpx.Response(503, headers={"Retry-After": "9"}))
    with pytest.raises(ProviderPollingRetryable) as error:
        retry.poll(request(), poll_sequence=1)
    assert error.value.retry_after == 9


def test_cancel_and_side_effect_free_connection_probe():
    cancelled = provider(lambda _: httpx.Response(204))
    assert cancelled.cancel(request()).status == "cancelled"
    def not_found(http_request):
        assert http_request.url.path == "/v1/tasks/00000000-0000-4000-8000-000000000000"
        return httpx.Response(404, json={"error": "not found"})

    authenticated = provider(not_found)
    assert authenticated.test_connection()["ok"] is True
    rejected = provider(lambda _: httpx.Response(401, json={"error": "invalid key"}))
    assert rejected.test_connection()["ok"] is False


def test_provider_status_never_returns_secret(client):
    response = client.get("/api/video-providers")
    assert response.status_code == 200
    text = response.text.lower()
    assert "api_secret" not in text and "test-secret" not in text
    runway = next(item for item in response.json()["providers"] if item["id"] == "Runway")
    assert runway["capabilities"]["duration_min"] == 2
    assert runway["capabilities"]["duration_max"] == 10
