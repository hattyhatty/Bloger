"""Runway Dev Gen-4.5 adapter.

Credentials are loaded only from backend settings. The adapter consumes the
immutable GenerationRequest snapshot and never reads mutable planner records.
"""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

import httpx

from .config import Settings, get_settings
from .providers import (ProviderCapabilities, ProviderOutcome, ProviderPollingRetryable,
                        ProviderRateLimited, ProviderUnavailable, VideoProviderAdapter)


RUNWAY_CAPABILITIES = ProviderCapabilities(
    provider="Runway",
    models=("gen4.5",),
    text_to_video=True,
    image_to_video=True,
    reference_image=True,
    negative_prompt=False,
    cancellation=True,
    reconciliation=True,
    webhook=False,
    duration_min=2,
    duration_max=10,
    text_ratios=("1280:720", "720:1280"),
    image_ratios=("1280:720", "1584:672", "1104:832", "720:1280", "832:1104", "672:1584", "960:960"),
    supported_resolutions=("720p",),
)


class RunwayVideoProvider(VideoProviderAdapter):
    capabilities = RUNWAY_CAPABILITIES

    def __init__(self, settings: Settings | None = None, client: httpx.Client | None = None):
        self.settings = settings or get_settings()
        self.client = client or httpx.Client(timeout=self.settings.runway_timeout_seconds)

    @property
    def configured(self) -> bool:
        return bool(self.settings.runwayml_api_secret.strip())

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.runwayml_api_secret.strip()}",
            "Content-Type": "application/json",
            "X-Runway-Version": self.settings.runway_api_version,
        }

    def _url(self, path: str) -> str:
        base = self.settings.runway_base_url.rstrip("/")
        parsed = urlparse(base)
        if parsed.scheme != "https" or parsed.hostname != "api.dev.runwayml.com":
            raise ProviderUnavailable("Runway Base URL must be https://api.dev.runwayml.com/v1")
        return base + path

    def _require_config(self):
        if not self.configured:
            raise ProviderUnavailable("Runway credential is not configured")
        self._url("")

    @staticmethod
    def _retry_after(response: httpx.Response) -> int | None:
        value = (response.headers.get("Retry-After") or "").strip()
        if not value:
            return None
        try:
            return max(0, int(float(value)))
        except ValueError:
            try:
                stamp = parsedate_to_datetime(value)
                if stamp.tzinfo is None:
                    stamp = stamp.replace(tzinfo=timezone.utc)
                return max(0, int((stamp - datetime.now(timezone.utc)).total_seconds()))
            except (TypeError, ValueError, OverflowError):
                return None

    @staticmethod
    def _json(response: httpx.Response) -> dict:
        try:
            value = response.json()
            return value if isinstance(value, dict) else {"data": value}
        except ValueError:
            return {"statusCode": response.status_code}

    @staticmethod
    def _error(response: httpx.Response) -> str:
        payload = RunwayVideoProvider._json(response)
        detail = payload.get("error") or payload.get("message") or payload.get("detail")
        if isinstance(detail, dict):
            detail = detail.get("message") or detail.get("type")
        suffix = f": {str(detail)[:400]}" if detail else ""
        return f"Runway HTTP {response.status_code}{suffix}"

    @staticmethod
    def _reference(request) -> str:
        config = request.generation_config or {}
        reference_id = str(config.get("reference_asset_id") or "")
        references = [item for item in (request.input_snapshot or {}).get("reference_assets", [])
                      if item.get("status") == "active"]
        if reference_id:
            references = [item for item in references if item.get("id") == reference_id]
            if not references:
                raise ProviderUnavailable("Selected reference asset is not linked to this Shot snapshot")
        if not references:
            return ""
        value = str(references[0].get("reference_url") or "").strip()
        if not value:
            raise ProviderUnavailable("Runway requires a public HTTPS reference URL; local file references are not uploaded")
        parsed = urlparse(value)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ProviderUnavailable("Runway reference must be a public HTTPS URL")
        return value

    def build_payload(self, request) -> dict:
        config = request.generation_config or {}
        snapshot = request.input_snapshot or {}
        prompt = snapshot.get("prompt") or {}
        generic = str(prompt.get("genericVideoPrompt") or prompt.get("generic_video_prompt") or "").strip()
        continuity = str(prompt.get("continuityNotes") or prompt.get("continuity_notes") or "").strip()
        text = "\n\n".join(value for value in (generic, continuity) if value)
        if not text:
            raise ProviderUnavailable("Generation Prompt is empty")
        model = request.model or self.settings.runway_default_model
        if model not in self.capabilities.models:
            raise ProviderUnavailable(f"Unsupported Runway model: {model}")
        shot = snapshot.get("shot") or {}
        duration = int(config.get("duration") or shot.get("estimatedDurationSeconds") or shot.get("estimated_duration_seconds") or 5)
        if not self.capabilities.duration_min <= duration <= self.capabilities.duration_max:
            raise ProviderUnavailable("Runway Gen-4.5 duration must be between 2 and 10 seconds")
        ratio_map = {"16:9": "1280:720", "9:16": "720:1280", "1:1": "960:960"}
        ratio = str(config.get("ratio") or ratio_map.get((snapshot.get("video_plan") or {}).get("aspect_ratio"), "1280:720"))
        reference = self._reference(request)
        supported = self.capabilities.image_ratios if reference else self.capabilities.text_ratios
        if ratio not in supported:
            raise ProviderUnavailable(f"Ratio {ratio} is not supported for this Runway generation mode")
        payload = {"model": model, "promptText": text, "ratio": ratio, "duration": duration}
        if reference:
            payload["promptImage"] = reference
        return payload

    def submit(self, request, *, on_dispatch, technical_attempt=1):
        self._require_config()
        payload = self.build_payload(request)
        on_dispatch()
        try:
            response = self.client.post(self._url("/image_to_video"), headers=self._headers(), json=payload)
        except httpx.RequestError as exc:
            raise ProviderUnavailable(f"Runway submit transport error: {exc.__class__.__name__}", dispatched=True) from exc
        if response.status_code == 429:
            raise ProviderRateLimited("Runway rate limit", retry_after=self._retry_after(response),
                dispatched=True, safe_to_resubmit=True)
        if response.status_code in {502, 503, 504}:
            raise ProviderUnavailable(self._error(response), dispatched=True)
        body = self._json(response)
        if response.status_code >= 400:
            return ProviderOutcome("failed", response=body, error=self._error(response))
        task_id = str(body.get("id") or "")
        if not task_id:
            return ProviderOutcome("unknown", response=body,
                error="Runway accepted the request without a task ID")
        return ProviderOutcome("submitted", provider_job_id=task_id, response=body)

    def _read_task(self, request) -> ProviderOutcome:
        self._require_config()
        if not request.provider_job_id:
            return ProviderOutcome("unknown",
                error="manual_reconciliation_required: Runway task ID is unavailable")
        try:
            response = self.client.get(self._url(f"/tasks/{request.provider_job_id}"), headers=self._headers())
        except httpx.RequestError as exc:
            raise ProviderPollingRetryable(f"Runway status transport error: {exc.__class__.__name__}") from exc
        if response.status_code in {429, 502, 503, 504}:
            raise ProviderPollingRetryable(self._error(response), retry_after=self._retry_after(response))
        body = self._json(response)
        if response.status_code >= 400:
            return ProviderOutcome("failed", provider_job_id=request.provider_job_id,
                response=body, error=self._error(response))
        status = str(body.get("status") or "").upper()
        if status in {"PENDING", "THROTTLED", "RUNNING"}:
            return ProviderOutcome("pending", provider_job_id=request.provider_job_id, response=body)
        if status == "SUCCEEDED":
            outputs = body.get("output") if isinstance(body.get("output"), list) else []
            result_url = str(outputs[0]) if outputs else ""
            if not result_url:
                return ProviderOutcome("unknown", provider_job_id=request.provider_job_id,
                    response=body, error="Runway task succeeded without an output URL")
            return ProviderOutcome("succeeded", provider_job_id=request.provider_job_id,
                result_url=result_url, response=body)
        if status == "FAILED":
            failure = body.get("failure") or body.get("failureCode") or "Runway generation failed"
            return ProviderOutcome("failed", provider_job_id=request.provider_job_id,
                response=body, error=str(failure)[:500])
        if status == "CANCELED":
            return ProviderOutcome("cancelled", provider_job_id=request.provider_job_id, response=body)
        return ProviderOutcome("unknown", provider_job_id=request.provider_job_id,
            response=body, error=f"Unrecognized Runway task status: {status or 'missing'}")

    def poll(self, request, *, poll_sequence):
        return self._read_task(request)

    def poll_interval_seconds(self, request) -> int:
        # Runway recommends five seconds or longer plus jitter. Queue backoff
        # provides the jitter-free minimum; technical retries add backoff.
        return max(5, int((request.generation_config or {}).get("poll_interval_seconds", 5)))

    def reconcile(self, request):
        return self._read_task(request)

    def cancel(self, request):
        self._require_config()
        if not request.provider_job_id:
            return ProviderOutcome("unsupported", error="Runway task ID is unavailable")
        try:
            response = self.client.delete(self._url(f"/tasks/{request.provider_job_id}"), headers=self._headers())
        except httpx.RequestError as exc:
            raise ProviderPollingRetryable(f"Runway cancellation transport error: {exc.__class__.__name__}") from exc
        if response.status_code in {429, 502, 503, 504}:
            raise ProviderPollingRetryable(self._error(response), retry_after=self._retry_after(response))
        if response.status_code >= 400:
            return ProviderOutcome("failed", provider_job_id=request.provider_job_id,
                response=self._json(response), error=self._error(response))
        return ProviderOutcome("cancelled", provider_job_id=request.provider_job_id,
            response={"statusCode": response.status_code})

    def test_connection(self) -> dict:
        self._require_config()
        # A known-absent task lookup validates URL, TLS and authorization without
        # creating a billable generation. 404 means authentication was accepted.
        probe = "00000000-0000-0000-0000-000000000000"
        try:
            response = self.client.get(self._url(f"/tasks/{probe}"), headers=self._headers())
        except httpx.RequestError as exc:
            return {"ok": False, "message": f"Connection failed: {exc.__class__.__name__}"}
        if response.status_code == 404:
            return {"ok": True, "message": "Runway authentication accepted (read-only probe)"}
        if response.status_code == 401:
            return {"ok": False, "message": "Runway authentication rejected"}
        if response.status_code == 429:
            return {"ok": False, "message": "Runway reachable but rate limited"}
        return {"ok": response.is_success, "message": f"Runway probe HTTP {response.status_code}"}
